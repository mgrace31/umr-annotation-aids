from sentence_transformers import SentenceTransformer
from statistics import mean

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = ['Edmund Pope tasted freedom today for the first time in more than eight months.',
             'Pope was flown to the U.S. military base at Ramstein, Germany.',
             'Pope was in remission from a rare form of bone cancer when he was arrested in Russia.',
             'A spokeswoman said that Pope was suffering from malnutrition and high blood pressure.',
             "Marsha Lipman is Editor of Moscow based news magazine 'Itogi'.",
             'Elvis Costello regarded acclaim and women with equal suspicion.',
             'For a while, they could do anything, at home with tub-thumpers like “Pump It Up” and midtempo flourishes like “Accidents Will Happen.”',
             'History repeats the old conceits.',
             'Not that a songwriter as steeped in pop history as Costello has needed American hits.',
             'The question mark was surely asking for trouble.']

mod_neg = ['Edmund Pope did not taste freedom today for the first time in more than eight months.',
           'Pope was not flown to the U.S. military base at Ramstein, Germany.',
           'Pope was not in remission from a rare form of bone cancer when he was arrested in Russia.',
           'A spokeswoman said that Pope was not suffering from malnutrition and high blood pressure.',
           "Marsha Lipman is not Editor of Moscow based news magazine 'Itogi'.",
           'Elvis Costello did not regard acclaim and women with equal suspicion.',
           'For a while, they could not do everything, at home with tub-thumpers like “Pump It Up” and midtempo flourishes like “Accidents Will Happen.”',
           'History does not repeat the old conceits.',
           'A songwriter as steeped in pop history as Costello has needed American hits.',
           'The question mark was not surely asking for trouble.']

mod_ent = ['Callie Hernandez tasted freedom today for the first time in more than eight months.',
           'Pope was flown to the U.S. military base in Prague, Czech Republic.',
           'Pope was in remission from a rare autoimmune disease when he was arrested in Russia.',
           'An on-the-ground reporter said that Pope was suffering from malnutrition and high blood pressure.',
           "Marsha Lipman is Editor of Moscow based news magazine 'Izvestiya'.",
           'Elvis Costello regarded acclaim and bandmates with equal suspicion.',
           'For a while, they could do anything, at home with tub-thumpers like “Pump It Up” and midtempo flourishes like “Just What I Needed.”',
           'History repeats the old charms.',
           'Not that a songwriter as steeped in pop history as Bush has needed American hits.',
           'The semicolon was surely asking for trouble.']

mod_ten = ['Edmund Pope is tasting freedom today for the first time in more than eight months .',
           'Pope is being flown to the U.S. military base at Ramstein, Germany.',
           'Pope will be in remission from a rare form of bone cancer when he is arrested in Russia.',
           'A spokeswoman said that Pope had suffered from malnutrition and high blood pressure.',
           "Marsha Lipman will be Editor of Moscow based news magazine 'Itogi'.",
           'Elvis Costello regards acclaim and women with equal suspicion.',
           'For a while, they will be able to do anything, at home with tub-thumpers like “Pump It Up” and midtempo flourishes like “Accidents Will Happen.”',
           'History repeated the old conceits.',
           'Not that a songwriter as steeped in pop history as Costello needs American hits.',
           'The question mark is surely asking for trouble.']

mod_asp = ['Edmund Pope tasted freedom for only six years of his adult life.',
           'Pope used to be flown to the U.S. military base at Ramstein, Germany.',
           'Pope was in remission from a rare form of bone cancer every two years.',
           'A spokeswoman said that Pope was suffering from malnutrition and high blood pressure every morning.',
           "Marsha Lipman is Editor of Moscow based news magazine 'Itogi' every Summer.",
           'Elvis Costello regarded acclaim and women with equal suspicion every time his new record came out.',
           'Once every five years, they could do anything, at home with tub-thumpers like “Pump It Up” and midtempo flourishes like “Accidents Will Happen.”',
           'History repeats the old conceits once.',
           'Not that a songwriter as steeped in pop history as Costello needed American hits in the 1980s.',
           'The question mark surely asked for trouble daily.']

mod_str = ['Today, Edmund Pope walked free after an eight-month sentence.',
           'The U.S. military base at Ramstein, Germany received the plane with Pope.',
           "During his arrest in Russia, Pope's rare form of bone cancer was in remission.",
           'Extreme hunger and high blood pressure were impacting Pope, a spokeswoman commented.',
           "The editor of the news magazine 'Itogi,' based in Moscow, is Marsha Lipman.",
           "Acclaim and women were equally suspicious in Elvis Costello's mind.",
           'At home with tub-thumpers like “Pump It Up” and midtempo flourishes like “Accidents Will Happen,” they were capable of anything for a while.',
           'The old conceits are repeated by history.',
           "It's not like Costello, being a songwriter as steeped in pop history as he was, has needed American hits.",
           'Surely, the question mark was asking for trouble.']

mods = [mod_neg, mod_ent, mod_ten, mod_asp, mod_str]
shifts = ['Negation','Entity Shift','Tense Shift','Aspect Shift','Restructuring']

os_embeddings = model.encode(sentences)
mod_embeddings = [model.encode(mod) for mod in mods]
similarities = [model.similarity(os_embeddings,me) for me in mod_embeddings]

mean_target_sims = [mean([similarities[i].tolist()[j][j] for j in range(len(sentences))]) for i in range(len(mods))]
for i in range(len(mean_target_sims)):
    print(f'{shifts[i]}: {"%.3f" % mean_target_sims[i]}')
