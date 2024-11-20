from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = ["Edmund Pope tasted freedom today for the first time in more than eight months.",
             "Mark Joseph Stern signed the document last week after a month of deliberation.",
             "Tory Pines stole a car today.",
             "Emma Eisenberg introduced a bill on Thursday for the first time since her election to Congress.",
             "Alan Best checked his bank account this morning.",
             "Elizabeth Holmes went to Amsterdam last night for a press conference.",
             "The Oregon Fire Department mitigated the wildfire this month after it had spread across local forests.",
             "Wanda takes a walk every morning.",
             "Paul Ohlinger used to cut down trees as his day job.",
             "Herman Abrams walked free on Monday after his parole was approved."]

embeddings = model.encode(sentences)
print(embeddings.shape)

similarities = model.similarity(embeddings, embeddings)
print(similarities)
