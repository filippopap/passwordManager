import os
import pickle
from cryptography.fernet import Fernet
from tkinter import filedialog, Tk
from termcolor import colored
import string
import random


def printColored(text, origin="[INFO]"):
    if origin == "[QUEST]":
        return input(colored(origin + '\t:\t ' + text, "green"))
    elif origin == "[RIEP]":
        print(colored(origin + '\t:\t ' + text, "yellow"))
    elif origin == "[INFO]":
        print(colored(origin + '\t:\t ' + text, "cyan"))
    elif origin == "[ERROR]":
        print(colored(origin + '\t:\t ' + text, "red"))


def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)


def load_key():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Seleziona il file chiave segreta")
    with open(file_path, "rb") as key_file:
        key = key_file.read()
    printColored("secret.key caricato con successo!")
    return key


def new_strong_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(8))
    return password


def encrypt_password(password, key):
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password


def decrypt_password(encrypted_password, key):
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password


def save_passwords(passwords, key):
    with open("passwords.dat", "wb") as password_file:
        encrypted_data = list()
        for service, username, password in passwords:
            encrypted_service = encrypt_password(service, key)
            encrypted_username = encrypt_password(username, key)
            encrypted_password = encrypt_password(password, key)
            encrypted_data.append((encrypted_service, encrypted_username, encrypted_password))
        pickle.dump(encrypted_data, password_file)


def load_passwords(key):
    passwords = list()
    if os.path.exists("passwords.dat"):
        with open("passwords.dat", "rb") as password_file:
            encrypted_data = pickle.load(password_file)
            for encrypted_service, encrypted_username, encrypted_password in encrypted_data:
                service = decrypt_password(encrypted_service, key)
                username = decrypt_password(encrypted_username, key)
                password = decrypt_password(encrypted_password, key)
                passwords.append((service, username, password))
    return passwords


def add_password(passwords, key):
    service = printColored("Inserisci il nome del servizio: ", "[QUEST]")
    username = printColored("Inserisci il nome utente: ", "[QUEST]")
    password = printColored("Inserisci la password o digitare 'pw' per "
                            "farla generare in automatico: ", "[QUEST]")
    if password.strip().upper() == "PW":
        password = new_strong_password()
    passwords.append((service, username, password))
    save_passwords(passwords, key)
    printColored("Password salvata con successo!")


def view_password(passwords):
    for i, (service, username, password) in enumerate(passwords):
        printColored(str(i + 1) + ": " + service, "[RIEP]")
    service_name = printColored("Inserisci il nome del servizio (o il numero corrispondente) per visualizzare la "
                                "password: ", "[QUEST]")
    for service, username, password in passwords:
        if service == service_name:
            printColored("Servizio: " + service, "[RIEP]")
            printColored("Nome Utente: " + username, "[RIEP]")
            printColored("Password: " + password, "[RIEP]")
            break
    else:
        try:
            service_name = int(service_name) - 1
            printColored("Servizio: " + passwords[service_name][0], "[RIEP]")
            printColored("Nome Utente: " + passwords[service_name][1], "[RIEP]")
            printColored("Password: " + passwords[service_name][2], "[RIEP]")
        except:
            printColored("Servizio " + service_name + " non trovato.", "[ERROR]")


def edit_password(passwords, key):
    service_name = printColored("Inserisci il nome del servizio per modificare le credenziali: ", "[QUEST]")

    for service, username, password in passwords:
        if service == service_name:
            printColored("Servizio: " + service, "[RIEP]")
            new_service = printColored("Nuovo Nome Servizio (premere invio per lasciare invariato): ", "[QUEST]")
            if not new_service:
                new_service = service
            printColored("Nome Utente: " + username, "[RIEP]")
            new_user = printColored("Nuovo Nome Utente (premere invio per lasciare invariato): ", "[QUEST]")
            if not new_user:
                new_user = username
            printColored("Password: " + password, "[RIEP]")
            new_password = printColored("Nuova Password (premere invio per lasciare invariato) o digitare 'pw' per "
                                        "farla generare in automatico: ", "[QUEST]")
            if not new_password:
                new_password = password
            elif password.strip().upper() == "PW":
                password = new_strong_password()
            target_tuple = (service, username, password)
            index_to_remove = next((i for i, entry in enumerate(passwords) if entry == target_tuple), None)

            if index_to_remove is not None:
                passwords.pop(index_to_remove)
            passwords.append((new_service, new_user, new_password))
            save_passwords(passwords, key)
            break
    else:
        printColored("Servizio " + service_name + " non trovato.", "[ERROR]")


def delete_service(passwords, key):
    service_name = printColored("Inserisci il nome del servizio per eliminarlo: ", "[QUEST]")

    for service, username, password in passwords:
        if service == service_name:
            printColored("Servizio: " + service, "[RIEP]")
            printColored("Nome Utente: " + username, "[RIEP]")
            printColored("Password: " + password, "[RIEP]")
            sure = printColored("Sei sicuro di voler eliminare questo servizio? (SI/NO)", "[QUEST]").strip().upper()
            if sure == "SI" or sure == "S":
                target_tuple = (service, username, password)
                index_to_remove = next((i for i, entry in enumerate(passwords) if entry == target_tuple), None)

                if index_to_remove is not None:
                    passwords.pop(index_to_remove)
                    printColored("Servizio " + service + " eliminato con successo!")
                    save_passwords(passwords, key)
            break
    else:
        printColored("Servizio " + service_name + " non trovato.", "[ERROR]")


def list_services(passwords):
    if not passwords:
        printColored("Nessun servizio salvato.", "[ERROR]")
    else:
        printColored("Elenco dei servizi salvati:")
        for service, _, _ in passwords:
            printColored(service, "[RIEP]")


def main():
    choice = printColored("Hai già una chiave segreta? (SI/NO): ", "[QUEST]").strip().upper()
    if choice == "SI" or choice == "S":
        printColored("Seleziona il file secret.key")
        key = load_key()
    elif choice == "NO" or choice == "N":
        printColored("Chiave generata (secret.key). NASCONDILA E CONSERVALA, serve a recuperare le tue password!")
        generate_key()
        printColored("Ora seleziona il file secret.key")
        key = load_key()
    else:
        return

    passwords = load_passwords(key)

    while True:
        printColored("Menu:")
        printColored("1. Aggiungi nuovo servizio, username e password")
        printColored("2. Visualizza le credenziali di un servizio")
        printColored("3. Modifica le credenziali di un servizio")
        printColored("4. Elimina un servizio")
        printColored("5. Esci")
        choice = printColored("Scegli un'opzione? (1/2/3/4/5): ", "[QUEST]").strip()

        if choice == "1":
            add_password(passwords, key)
        elif choice == "2":
            view_password(passwords)
        elif choice == "3":
            edit_password(passwords, key)
        elif choice == "4":
            delete_service(passwords, key)
        elif choice == "5":
            printColored("Arrivederci!")
            break
        else:
            printColored("Scelta non valida. Si prega di rispondere con 1, 2, 3, 4 o 5"
                         ".", "[ERROR]")


if __name__ == "__main__":
    main()
