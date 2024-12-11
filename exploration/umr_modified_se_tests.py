import csv
from sentence_transformers import SentenceTransformer

def readcsv(filename,column):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        strings = [row[column] for row in reader]
    csvfile.close()
    return strings

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = readcsv('altered_sentences.csv','Original Sentence')
mphrases = readcsv('altered_sentences.csv','Modified Phrase')

os_embeddings = model.encode(sentences)
mp_embeddings = model.encode(mphrases)

similarities = model.similarity(os_embeddings,mp_embeddings)
print(similarities)

similarities = similarities.tolist()
max_sims = [row.index(max(row)) for row in similarities]
from_sentence = [similarities[ind][ind] == similarities[ind][max_sims[ind]] for ind in range(len(max_sims))]
prop_from_sentence = sum([match for match in from_sentence if match])/len(from_sentence)

print(max_sims)
print(from_sentence)
print(prop_from_sentence)

non_aligned = {sentences[i]: mphrases[max_sims[i]] for i in range(len(max_sims)) if not from_sentence[i]}

for sent in non_aligned:
    print(f'{sent} ~ {non_aligned[sent]}')
