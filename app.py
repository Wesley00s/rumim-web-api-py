import firebase_admin
from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, firestore

app = FastAPI()

cred = credentials.Certificate("firebase/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


@app.get("/usuario/{id}")
async def get_usuario(id: str):
    usr_ref = db.collection('Usuarios').document(id)
    usr = usr_ref.get()

    if usr.exists:
        usuario_data = usr.to_dict()

        prop_ref = usr_ref.collection('Propriedades')
        prop_snapshots = prop_ref.get()

        propriedades_data = []
        for prop_snap in prop_snapshots:
            prop_data = prop_snap.to_dict()

            anim_ref = prop_snap.reference.collection('Animais')
            anim_snapshots = anim_ref.get()

            animais_data = []
            for anim_snap in anim_snapshots:
                anim_data = anim_snap.to_dict()
                animais_data.append(anim_data)

            prop_data['Animais'] = animais_data
            propriedades_data.append(prop_data)

        usuario_data['Propriedades'] = propriedades_data

        return usuario_data
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
