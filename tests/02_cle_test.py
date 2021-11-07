from config import DefaultConfig

def test_cle_insight():
    
    assert DefaultConfig.APPINSIGHTS_INSTRUMENTATION_KEY == 'e1695f15-df98-4bc0-918a-75dfb8c1aa79'
    
def test_cle_luis():
    
    assert DefaultConfig.LUIS_API_KEY == '7bccf58a81bf4e43bedb92e2272fe87f'
    
