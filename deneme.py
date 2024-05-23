from flask import Flask, jsonify, request, render_template
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import json

app = Flask(__name__)

def get_card_meanings(cards):
    with open("tarot.json", "r") as f:
        data = json.load(f)

    card_meanings = {}
    for card in cards:
        for item in data:
            if item["cardName"] == card["name"]:
                card_meanings[card["name"]] = item.get("cardMeaning", "")
                break

        if len(card_meanings) == len(cards):
            break

    return card_meanings

def combine_card_meanings(card_meanings):
    combined_description = ""
    for card_name, meaning in card_meanings.items():
        combined_description += f"{card_name}: {meaning}\n"
    return combined_description

@app.route("/")
def index():
    return render_template("index.html")  # index.html dosyasını render ediyor

@app.route("/api/v1/hello", methods=["POST"])
def hello_world():
    body = request.json
    print(body, type(body))

    name = request.args.get("name", "")
    gender = request.args.get("gender", "")
    fal_type = request.args.get("fal_type", "")

    cards = body.get("cards", [])
    card_names = [card["name"] for card in cards]
    card_meanings = get_card_meanings(cards)
    combined_description = combine_card_meanings(card_meanings)

    prompt = ChatPromptTemplate.from_template(f"""
    Sen bir tarot falcısısın.
    Kullanıcıya seçilen kartları paraphrase ederek {fal_type} açılımına uygun bir fal yorumu vermelisin.
    Fal yorumunu verirken kullanıcıya ve kendine farklı sıfatlar vererek fal yorumunu hikayeleştirmelisin. Daha eğlenceli hale getirmelisin! Örneğin: "Ben tarot kartlarının gizemli dünyasında yolculuk eden bir kahinim. Sen de benim falıma yolculuk edecek küçük dostumsun" gibi.
    Kullanıcının adı: {name} , cinsiyeti: {gender}.
    Uzun, açıklayıcı ve kullanıcıyı tatmin edecek bir yorumda bulunmalısın. 
    Arkadaşça ve esprili bir dil kullanmalısın.
    Kartlar:
    {card_names} 😊🔮
    """)

    model = GoogleGenerativeAI(model="models/gemini-pro", google_api_key="AIzaSyDJaTAAZhKq7Dlbu4smgA5suiroTxeuUUo", temperature=0.9)
    chain = prompt | model
    response = chain.invoke({"name": name, "gender": gender, "fal_type": fal_type, "cards": combined_description})

    return jsonify({"msg": response})

@app.route("/api/v1/hello1", methods=["POST"])
def hello_world1():
    body = request.json
    print(body, type(body))

    cards = body.get("cards", [])
    card_meanings = get_card_meanings(cards)
    combined_description = combine_card_meanings(card_meanings)

    return jsonify({"msg": combined_description})

if __name__ == '__main__':
    app.run()
