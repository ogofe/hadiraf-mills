from utils import fetch_settings

def hadiraf(request):
    settings = fetch_settings()
    return {
        'org_name' : settings["name_of_organisation"]
    }
    