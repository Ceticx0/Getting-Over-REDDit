import re


def run(playwright, post_link):
    """Opens a reddit post, and screenshots the post and the first few comments then returns the post text, indentation
    and upvote count abbreviated"""
    print(f"Screenshotting post {post_link}")
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    page.goto(post_link)
    print("Page loaded")
    # get all post and comment elements
    try:
        post = page.locator('data-testid=post-container')
        comments = page.query_selector_all('div[data-testid="comment"]')
    except TimeoutError:  # if it times out, try reloading the page, otherwise return the exception
        page.reload()
        post = page.locator('data-testid=post-container')
        comments = page.query_selector_all('div[data-testid="comment"]')

    post.screenshot(path="media/post.png")
    print("items grabbed")
    regex = "/level \d/g"
    responses = []
    for index, comment in enumerate(comments):
        comment_parent = comment.query_selector("xpath=..")
        print(f"comment parent found: {comment_parent.text_content()[:50]}")
        # gets upvote count of post from text color
        upvotes = comment_parent.query_selector('div[style="color:#1A1A1B"]')
        if not upvotes:  # its different randomly sometimes
            upvotes = comment_parent.query_selector('div[style="color: rgb(26, 26, 27);"]').text_content()
        else:
            upvotes = upvotes.text_content()

        # extract the level count from all the text in the comment
        # would literally break if someone said "level x" in comment content
        # TODO: fix regex to not include post content
        level = re.match(r'level \d', comment_parent.text_content())
        comment_filepath = "media/comments/comment{}.png".format(index)
        responses.append((comment_filepath, comment.inner_text(), level.group()[6:], upvotes))
        try:
            comment_parent.screenshot(path=comment_filepath)
        except TimeoutError:
            print("Screenshotting timed out... Reloading web page")
            page.reload()
            page.wait_for_selector('div[data-testid="comment"]')
            comments = page.query_selector_all('div[data-testid="comment"]')
            comments = comments[index:]  # resume at previously indexed comment

        except Exception as e:
            print("--- screenshotting failed ---")
            print(f"Exceptions is: {e}")

    browser.close()
    return responses


if __name__ == '__main__':
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright_instance:
        responses = run(playwright_instance,
                        "https://reddit.com/r/AskReddit/comments/y3acfn/people_who_go_into_the_bathroom_to_freshen_up/")
        for path, text, indentation, upvote_count in responses:
            print("{} | {} - {}: {}".format(path, indentation, upvote_count, text.replace('\n', '[\\n]')))
