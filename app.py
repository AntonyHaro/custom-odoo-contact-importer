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
                "city": header.index("city"),
                "country_id":  header.index("country_id"),
                "state_id":  header.index("state_id"), 
                "street": header.index("street"),

                #custom contact fields "x_custom_field_name"
                "x_linkedin": header.index("x_linkedin"),
                "x_redes_sociais": header.index("x_redes_sociais"),
                "redes_sociais_empresa": header.index("redes_sociais_empresa"),
                "x_setor": header.index("x_setor"),
                
                # contact's company info
                "setor_empresa": header.index("setor_empresa"),
                "url_empresa":  header.index("url_empresa"),
                "telefone_sede":  header.index("telefone_sede"),
                "tamanho_empresa":  header.index("tamanho_empresa"),
                "local_empresa": header.index("local_empresa"),
            }

            contacts = []
            invalid_contacts = []
            
            # check the valid records in the csv file
            print("\nRegistros válidos do arquivo:")
            for row_index, row in enumerate(reader, start=1):    

                # create the contact object based on the contact_indexes info 
                contact = {
                    "name": row[contact_indexes["name"]].strip(),
                    "email": row[contact_indexes["email"]].strip(),
                    "function": row[contact_indexes["function"]].strip(),
                    "company_name": row[contact_indexes["company_name"]].strip(),
                    "city": row[contact_indexes["city"]].strip(),
                    "country_id": row[contact_indexes["country_id"]].strip(),
                    "state_id": row[contact_indexes["state_id"]].strip(),
                    "street": row[contact_indexes["street"]].strip(),
                    
                    "x_linkedin": row[contact_indexes["x_linkedin"]].strip(),
                    "x_redes_sociais": row[contact_indexes["x_redes_sociais"]].strip(),
                    "x_setor": row[contact_indexes["x_setor"]].strip(),

                    # single field with general company info (type text)
                    "x_info_empresa": f"""
                        Nome: {row[contact_indexes["company_name"]].strip()}
                        Localização: {row[contact_indexes["local_empresa"]].strip()}
                        Telefone da sede: {row[contact_indexes["telefone_sede"]].strip()}
                        Redes Sociais: {row[contact_indexes["redes_sociais_empresa"]].strip()}
                        Setor: {row[contact_indexes["setor_empresa"]].strip()}
                        Tamanho: {row[contact_indexes["tamanho_empresa"]].strip()}
                        URL: {row[contact_indexes["url_empresa"]].strip()}
                    """
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
            country_id = get_country_id(models, db, uid, password, contact["country_id"])
            if country_id:
                contact["country_id"] = country_id

            state_id = get_state_id(models, db, uid, password, country_id, contact["state_id"])
            if state_id:
                contact["state_id"] = state_id

            # create the contact using the res.partner model and print the contact_id
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