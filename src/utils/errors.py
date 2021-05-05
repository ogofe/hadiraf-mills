


class Error(Exception):
    name = None
    message = None

    def __str__(self):
    	return self.message
    
class SettingNotFoundError(Error):
    name = "setting_404"
    message = "Setting Not Found"
    
class IntentionalError(Error):
	name = "testing_error"
	message = "This is an intentional error used for debugging and testing"