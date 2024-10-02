import xmlrpc.client
import csv
import os
from dotenv import load_dotenv
from get_ids import get_country_id, get_state_id

load_dotenv()

# import csv data and return an array of contacts (contacts are the objects)
def import_csv_contacts(file_name):
    print(f"Diretório atual: {os.getcwd()}")
    
    try:
        if not os.path.isfile(file_name):
            print(f"Arquivo '{file_name}' não encontrado no diretório atual.")
            return
        
        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            # collect the csv headers and set the header indexes in contact_indexes object
            contact_indexes = {
                #defualt res.partner fields
                "name": header.index("name"),
                "email": header.index("email"),
                "function": header.index("function"),
                "company_name": header.index("company_name"),

                #custom fields "x_customfieldname"
                "x_linkedin": header.index("x_linkedin"),
                "x_redes_sociais_contato": header.index("x_redes_sociais_contato"),
                "x_redes_sociais_empresa": header.index("x_redes_sociais_empresa"),
                "x_setor_contato": header.index("x_setor_contato"),
                "x_setor_empresa": header.index("x_setor_empresa")
            }

            contacts = []
            invalid_contacts = []
            
            # check the valid records in the csv file
            print("\nRegistros válidos do arquivo:")
            for row_index, row in enumerate(reader, start=1):    
                
                contact = {
                    "name": row[contact_indexes["name"]].strip(),
                    "email": row[contact_indexes["email"]].strip(),
                    "function": row[contact_indexes["function"]].strip(),
                    "company_name": row[contact_indexes["company_name"]].strip(),
                    "x_linkedin": row[contact_indexes["x_linkedin"]].strip(),
                    "x_redes_sociais_contato": row[contact_indexes["x_redes_sociais_contato"]].strip(),
                    "x_redes_sociais_empresa": row[contact_indexes["x_redes_sociais_empresa"]].strip(),
                    "x_setor_contato": row[contact_indexes["x_setor_contato"]].strip(),
                    "x_setor_empresa": row[contact_indexes["x_setor_empresa"]].strip()
                }

                if not contact["name"] or not contact["email"]:
                    invalid_contacts.append(f"Registro {row_index}")
                    continue

                print(f"Registro {row_index}, Nome: {contact['name']}, Email: {contact['email']}")
                contacts.append(contact)
                
            if len(invalid_contacts) > 0:
                print("\nRegistros inválidos:")
                for i in invalid_contacts:
                    print(i)
            
            return contacts

    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")

# authenticate the user information to return uid
def authenticate(url, db, username, password):
    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        if not uid: 
            raise ValueError("Falha na autenticação. Verifique as credenciais.")
        return uid
    
    except Exception as e:
        print(f"Erro ao autenticar: {e}")

# create the contacts based on the contacts array
def create_contacts(url, db, uid, password, contacts):
    try: 
        models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))

        for contact in contacts:
            if not contact.get("name") or not contact.get("email"):
                print(f"Contato inválido, faltando nome ou email: {contact}")
                continue

            contact_id = models.execute_kw(db, uid, password, "res.partner", "create", [contact])
            print(f"Contato criado com o ID: {contact_id}")
        
    except Exception as e:
        print(f"Erro ao criar contatos: {e}")

def main():
    # get the credentials
    odoo_url = os.getenv("ODOO_URL")
    odoo_db = os.getenv("ODOO_DB")
    odoo_username = os.getenv("ODOO_USERNAME")
    odoo_password = os.getenv("ODOO_PASSWORD")

    # try to authenticate the user and get the uid
    uid = authenticate(odoo_url, odoo_db, odoo_username, odoo_password)
    if uid:
        # get the contacts from csv
        contacts = import_csv_contacts("file.csv")
        
        if contacts:
            print(f"\nTotal de contatos para serem carregados: {len(contacts)}\n")

            # create contacts from the array of contacts
            create_contacts(odoo_url, odoo_db, uid, odoo_password, contacts)
    
if __name__ == "__main__":
    main()