import json

def test_taille_testset():
    with open('./test_set.json') as f:
      essai = json.load(f)
    
    assert len(essai) == 155 
