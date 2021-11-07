# Microsoft Azure Language Understanding (LUIS) - Build App
#
# This script builds a LUIS app, entities, and intents using the Python
# LUIS SDK.  A separate sample trains and publishes the app.
#
# This script requires the Cognitive Services LUIS Python module:
#     python -m pip install azure-cognitiveservices-language-luis
#
# This script runs under Python 3.4 or later.

# Be sure you understand how LUIS models work.  In particular, know what
# intents, entities, and utterances are, and how they work together in the
# context of a LUIS app. See the following:
#
# https://www.luis.ai/welcome
# https://docs.microsoft.com/azure/cognitive-services/luis/luis-concept-intent
# https://docs.microsoft.com/azure/cognitive-services/luis/luis-concept-entity-types
# https://docs.microsoft.com/azure/cognitive-services/luis/luis-concept-utterance

# <Dependencies>
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from msrest.authentication import CognitiveServicesCredentials

import datetime, json, os, time
# </Dependencies>

# <AuthorizationVariables>
authoring_key = '7bccf58a81bf4e43bedb92e2272fe87f'

authoring_endpoint = 'https://westus.api.cognitive.microsoft.com/'
# </AuthorizationVariables>

# <Client>
# Instantiate a LUIS client
client = LUISAuthoringClient(authoring_endpoint, CognitiveServicesCredentials(authoring_key))
# </Client>

# <createApp>
def create_app():
	# Create a new LUIS app
	app_name    = "LuisP10_app {}".format(datetime.datetime.now())
	app_desc    = "Projet 10: MVP Flight booking app."
	app_version = "0.1"
	app_locale  = "en-us"

	app_id = client.apps.add(dict(name=app_name,
									initial_version_id=app_version,
									description=app_desc,
									culture=app_locale))

	print("Created LUIS app {}\n    with ID {}".format(app_name, app_id))
	return app_id, app_version
# </createApp>

# Declare entities:
#
#   From - ville de départ
#   To - ville d'arrivée
#   ondate - date aller  
#   backdate - date retour
#   money - budget maximum
#
#
# Creating an entity (or other LUIS object) returns its ID.
# We don't use IDs further in this script, so we don't keep the return value.
# <addEntities>
def add_entities(app_id, app_version):
    fromEntityId = client.model.add_entity(app_id, app_version, name="From")
    print("fromEntityId {} added.".format(fromEntityId))
    
    toEntityId = client.model.add_entity(app_id, app_version, name="To")
    print("toEntityId {} added.".format(toEntityId))
    
    ondateEntityId = client.model.add_entity(app_id, app_version, name="Ondate")
    print("ondateEntityId {} added.".format(ondateEntityId))
    
    backdateEntityId = client.model.add_entity(app_id, app_version, name="Backdate")
    print("backdateEntityId {} added.".format(backdateEntityId))
    
    moneyEntityId = client.model.add_entity(app_id, app_version, name="Money")
    print("moneyEntityId {} added.".format(moneyEntityId))

    

# </addEntities>

# Declare an intent, BookFlights, that recognizes a user's Flight request
# Creating an intent returns its ID, which we don't need, so don't keep.
# <addIntents>
def add_intents(app_id, app_version):
	intentId = client.model.add_intent(app_id, app_version, "BookFlights")

	print("Intent BookFlights {} added.".format(intentId))
# </addIntents>


# Helper function for creating the utterance data structure.
# <createUtterance>
def create_utterance(intent, utterance, *labels):
    """Add an example LUIS utterance from utterance text and a list of
       labels.  Each label is a 2-tuple containing a label name and the
       text within the utterance that represents that label.

       Utterances apply to a specific intent, which must be specified."""

    text = utterance.lower()

    def label(name, value):
        value = value.lower()
        start = text.index(value)
        return dict(entity_name=name, start_char_index=start,
                    end_char_index=start + len(value))

    return dict(text=text, intent_name=intent,
                entity_labels=[label(n, v) for (n, v) in labels])
# </createUtterance>

# Add example utterances for the intent.  Each utterance includes labels
# that identify the entities within each utterance by index.  LUIS learns
# how to find entities within user utterances from the provided examples.
#
# Example utterance: "find flights in economy to Madrid"
# Labels: Flight -> "economy to Madrid" (composite of Destination and Class)
#         Destination -> "Madrid"
#         Class -> "economy"
# <addUtterances>
def add_utterances(app_id, app_version):
	# Now define the utterances
	utterances = [create_utterance("BookFlights", "book flight from London to Paris on May 22, 2021 returning june 21, 2021 for $200",
							("From", "London"),
							("To", "Paris"),
                            ("Ondate", "May 22, 2021"),
                            ("Backdate", "june 21, 2021"),
							("Money", "$200"))]

	# Add the utterances in batch. You may add any number of example utterances
	# for any number of intents in one call.
	client.examples.batch(app_id, app_version, utterances)
	print("{} example utterance(s) added.".format(len(utterances)))
# </addUtterances>

# <train>
def train_app(app_id, app_version):
	response = client.train.train_version(app_id, app_version)
	waiting = True
	while waiting:
		info = client.train.get_status(app_id, app_version)

		# get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
		waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
		if waiting:
			print ("Waiting 10 seconds for training to complete...")
			time.sleep(10)
# </train>

# <publish>
def publish_app(app_id, app_version):
	responseEndpointInfo = client.apps.publish(app_id, app_version, is_staging=True)
	print("Application published. Endpoint URL: " + responseEndpointInfo.endpoint_url)
# </publish>

# <predict>
def predict(app_id, publishInfo, slot_name):

	request = { "query" : "Book flight to seattle" }

	# Note be sure to specify, using the slot_name parameter, whether your application is in staging or production.
	response = clientRuntime.prediction.get_slot_prediction(app_id=app_id, slot_name=slot_name, prediction_request=request)

	print("Top intent: {}".format(response.prediction.top_intent))
	#print("Sentiment: {}".format (response.prediction.sentiment))
	print("Intents: ")

	for intent in response.prediction.intents:
		print("\t{}".format (json.dumps (intent)))
	print("Entities: {}".format (response.prediction.entities))
# </predict>

print("Creating application...")
app_id, app_version = create_app()
print()

print ("Adding entities to application...")
add_entities(app_id, app_version)
print ()

print ("Adding intents to application...")
add_intents(app_id, app_version)
print ()

print ("Adding utterances to application...")
add_utterances(app_id, app_version)
print ()

print ("Training application...")
train_app(app_id, app_version)
print ()

print ("Publishing application...")
publish_app(app_id, app_version)