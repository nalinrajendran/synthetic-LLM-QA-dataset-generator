import ollama

# select from available ollama models
available_models = ollama.list()

# Get only the name from the REST API response
available_models=[model.model for model in available_models.models]
print("Available models: ", available_models)