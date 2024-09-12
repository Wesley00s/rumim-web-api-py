import firebase_admin
import uvicorn
from fastapi import FastAPI, HTTPException, Header
from firebase_admin import credentials, firestore
from fastapi.middleware.cors import CORSMiddleware

from firebase_auth import verify_firebase_token

app: FastAPI = FastAPI()

cred = credentials.Certificate("firebase/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    return verify_firebase_token(token)

@app.get("/user/{user_id}",
         summary="Obter informações do usuário",
         description="Retorna as informações básicas de um usuário pelo ID.")
def get_user_info(user_id: str):
    usr_ref = db.collection('Usuarios').document(user_id)
    usr = usr_ref.get()

    if usr.exists:
        user_data = usr.to_dict()
        return {
            "firstName": user_data.get("Nome"),
            "lastName": user_data.get("Sobrenome"),
            "occupation": user_data.get("Ocupação"),
            "dateOfBirth": user_data.get("Data de nascimento"),
            "email": user_data.get("Email")
        }
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

@app.get("/user/{user_id}/properties",
         summary="Obter informações das propriedades de um produtor",
         description="Retorna as informações básicas das propriedades pelo ID do produtor.")
def get_user_properties(user_id: str):
    usr_ref = db.collection('Usuarios').document(user_id)
    usr = usr_ref.get()

    if usr.exists:
        prop_ref = usr_ref.collection('Propriedades')
        prop_snapshots = prop_ref.get()

        properties_data = []
        for prop_snap in prop_snapshots:
            prop_data = prop_snap.to_dict()

            properties_data.append({
                "propertyLocation": prop_data.get("Localização da propriedade"),
                "smallRuminants": prop_data.get("Pequenos ruminantes"),
                "environmentalPractices": prop_data.get("Práticas ambientais"),
                "waterResources": prop_data.get("Recursos hídricos da propriedade"),
                "otherFarmAnimals": prop_data.get("Outras criações"),
                "areaInHectares": prop_data.get("Area em hectares"),
                "propertyName": prop_data.get("Nome da propriedade"),
                "technicalManager": prop_data.get("Responsável técnico")
            })

        return properties_data
    else:
        raise HTTPException(status_code=404, detail="User not found.")


@app.get("/user/{user_id}/property/{prop_id}/animals",
         summary="Obter informações dos animais especificos de uma propriedade",
         description="Retorna as informações básicas dos propriedades pelo ID do usuário e ID da propriedade.")
def get_animals_of_property(user_id: str, prop_id: str):
    usr_ref = db.collection('Usuarios').document(user_id)
    usr = usr_ref.get()

    if usr.exists:
        prop_ref = usr_ref.collection('Propriedades').document(prop_id)
        prop_snap = prop_ref.get()

        if prop_snap.exists:
            anim_ref = prop_ref.collection('Animais')
            anim_snapshots = anim_ref.get()

            animals_data = []
            for anim_snap in anim_snapshots:
                anim_data = anim_snap.to_dict()
                animals_data.append({
                    "currentWeight": anim_data.get("Peso atual"),
                    "dateOfBirth": anim_data.get("Data de nascimento"),
                    "birthWeight": anim_data.get("Peso ao nascimento"),
                    "breed": anim_data.get("Raça"),
                    "category": anim_data.get("Categoria"),
                    "weaningDate": anim_data.get("Data do desmame"),
                    "numberId": anim_data.get("Número de identificação"),
                    "gender": anim_data.get("Sexo"),
                    "animalImageUrl": anim_data.get("Url da imagem do animal"),
                    "animalStatus": anim_data.get("Status do animal"),
                    "weaningWeight": anim_data.get("Peso ao desmame")
                })

            return animals_data
        else:
            raise HTTPException(status_code=404, detail="Property not found.")
    else:
        raise HTTPException(status_code=404, detail="User not found.")


@app.get("/user/{user_id}/animals",
         summary="Obter todos os animais de um usuário",
         description="Retorna todos os animais de um usuário, independentemente da propriedade.")
def get_all_user_animals(user_id: str):
    usr_ref = db.collection('Usuarios').document(user_id)
    usr = usr_ref.get()

    if usr.exists:
        prop_ref = usr_ref.collection('Propriedades')
        prop_snapshots = prop_ref.get()

        all_animals = []
        for prop_snap in prop_snapshots:
            prop_id = prop_snap.id
            anim_ref = prop_ref.document(prop_id).collection('Animais')
            anim_snapshots = anim_ref.get()

            for anim_snap in anim_snapshots:
                anim_data = anim_snap.to_dict()
                all_animals.append({
                    "propertyName": prop_snap.to_dict().get("Nome da propriedade"),
                    "currentWeight": anim_data.get("Peso atual"),
                    "dateOfBirth": anim_data.get("Data de nascimento"),
                    "birthWeight": anim_data.get("Peso ao nascimento"),
                    "breed": anim_data.get("Raça"),
                    "category": anim_data.get("Categoria"),
                    "weaningDate": anim_data.get("Data do desmame"),
                    "numberId": anim_data.get("Número de identificação"),
                    "gender": anim_data.get("Sexo"),
                    "animalImageUrl": anim_data.get("Url da imagem do animal"),
                    "animalStatus": anim_data.get("Status do animal"),
                    "weaningWeight": anim_data.get("Peso ao desmame")
                })

        return all_animals
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")


@app.get("/animals",
         summary="Obter informações de todos os animais",
         description="Retorna todas as informações dos animais de todas as propriedades de todos os usuários.")
def get_all_animals():
    all_animals = []

    usr_ref = db.collection('Usuarios')
    usr_snapshots = usr_ref.get()

    for usr_snap in usr_snapshots:
        usr = usr_snap.to_dict()
        prop_ref = usr_snap.reference.collection('Propriedades')
        prop_snapshots = prop_ref.get()

        for prop_snap in prop_snapshots:
            prop = prop_snap.to_dict()
            anim_ref = prop_snap.reference.collection('Animais')
            anim_snapshots = anim_ref.get()

            for anim_snap in anim_snapshots:
                anim_data = anim_snap.to_dict()
                all_animals.append({
                    "userId": usr_snap.id,
                    "propertyName": prop.get("Nome da propriedade"),
                    "currentWeight": anim_data.get("Peso atual"),
                    "dateOfBirth": anim_data.get("Data de nascimento"),
                    "birthWeight": anim_data.get("Peso ao nascimento"),
                    "breed": anim_data.get("Raça"),
                    "category": anim_data.get("Categoria"),
                    "weaningDate": anim_data.get("Data do desmame"),
                    "numberId": anim_data.get("Número de identificação"),
                    "gender": anim_data.get("Sexo"),
                    "animalImageUrl": anim_data.get("Url da imagem do animal"),
                    "animalStatus": anim_data.get("Status do animal"),
                    "weaningWeight": anim_data.get("Peso ao desmame")
                })

    return all_animals

@app.get("/user/{user_id}/property/{prop_id}/animals/categories",
         summary="Obter quantidade de animais por categoria de uma propriedade específica",
         description="Retorna a quantidade de animais por categoria para uma propriedade específica do usuário.")
def get_animal_categories_by_property(user_id: str, prop_id: str):
    usr_ref = db.collection('Usuarios').document(user_id)
    usr = usr_ref.get()

    if usr.exists:
        prop_ref = usr_ref.collection('Propriedades').document(prop_id)
        prop_snap = prop_ref.get()

        if prop_snap.exists:
            anim_ref = prop_ref.collection('Animais')
            anim_snapshots = anim_ref.get()

            category_counts = {}

            for anim_snap in anim_snapshots:
                anim_data = anim_snap.to_dict()
                category = anim_data.get("Categoria")
                if category:
                    if category in category_counts:
                        category_counts[category] += 1
                    else:
                        category_counts[category] = 1

            return category_counts
        else:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada.")
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")


@app.get("/user/{user_id}/property/{prop_id}/animals/breeds",
         summary="Obter quantidade de animais por raça de uma propriedade específica",
         description="Retorna a quantidade de animais por raça para uma propriedade específica do usuário.")
def get_animal_breeds_by_property(user_id: str, prop_id: str):
    usr_ref = db.collection('Usuarios').document(user_id)
    usr = usr_ref.get()

    if usr.exists:
        prop_ref = usr_ref.collection('Propriedades').document(prop_id)
        prop_snap = prop_ref.get()

        if prop_snap.exists:
            anim_ref = prop_ref.collection('Animais')
            anim_snapshots = anim_ref.get()

            breed_counts = {}

            for anim_snap in anim_snapshots:
                anim_data = anim_snap.to_dict()
                breed = anim_data.get("Raça")
                if breed:
                    if breed in breed_counts:
                        breed_counts[breed] += 1
                    else:
                        breed_counts[breed] = 1

            return breed_counts
        else:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada.")
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")


@app.get("/user/{user_id}/property/{prop_id}/animals/genders",
         summary="Obter quantidade de animais por sexo de uma propriedade específica",
         description="Retorna a quantidade de animais por sexo para uma propriedade específica do usuário.")
def get_animal_genders_by_property(user_id: str, prop_id: str):
    usr_ref = db.collection('Usuarios').document(user_id)
    usr = usr_ref.get()

    if usr.exists:
        prop_ref = usr_ref.collection('Propriedades').document(prop_id)
        prop_snap = prop_ref.get()

        if prop_snap.exists:
            anim_ref = prop_ref.collection('Animais')
            anim_snapshots = anim_ref.get()

            gender_counts = {}

            for anim_snap in anim_snapshots:
                anim_data = anim_snap.to_dict()
                gender = anim_data.get("Sexo")
                if gender:
                    if gender in gender_counts:
                        gender_counts[gender] += 1
                    else:
                        gender_counts[gender] = 1

            return gender_counts
        else:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada.")
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")


@app.get("/user/{user_id}/property/{prop_id}/animals/total",
         summary="Obter o total de animais de uma propriedade",
         description="Retorna o número total de animais de uma propriedade específica do usuário.")
def get_total_animals_by_property(user_id: str, prop_id: str):
    usr_ref = db.collection('Usuarios').document(user_id)
    usr = usr_ref.get()

    if usr.exists:
        prop_ref = usr_ref.collection('Propriedades').document(prop_id)
        prop_snap = prop_ref.get()

        if prop_snap.exists:
            anim_ref = prop_ref.collection('Animais')
            anim_snapshots = anim_ref.get()

            total_animals = len(anim_snapshots)
            return {"totalAnimals": total_animals}
        else:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada.")
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)