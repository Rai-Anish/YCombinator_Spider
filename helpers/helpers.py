async def scroll_to_bottom(page):
    """
    Scrolls to the bottom of a page to load all dynamic content.
    
    Args:
        page: The Playwright page object.
        pause: Time in second to wait between scrolls to allow content to load. 
    """
    prev_height = 0
    new_height = await page.evaluate("() => document.body.scrollHeight")

    while prev_height != new_height:
        prev_height = new_height
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000) 
        new_height = await page.evaluate("() => document.body.scrollHeight")

def should_abort_request(request):
    if request.resource_type == 'image':
        return True

def batch_list():
    batches = [
    "F24", "S24", "W24", "S23", "W23", "S22", "W22", "S21", "W21", "S20", "W20",
    "S19", "W19", "S18", "W18", "S17", "W17", "IK12", "S16", "W16", "S15", "W15",
    "S14", "W14", "S13", "W13", "S12", "W12", "S11", "W11", "S10", "W10", "S09",
    "W09", "S08", "W08", "S07", "W07", "S06", "W06", "S05"
    ]
    return batches

def batch_url_generator():
    url = 'https://www.ycombinator.com/companies/?batch='
    batches = batch_list()
    url_list = []
    for batch in batches:
        new_url = url + batch
        url_list.append(new_url)

    return url_list
