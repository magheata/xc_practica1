from bs4 import BeautifulSoup
import requests
import multiprocessing

paper_link = 'https://www.medicinenet.com'

diseasesWithSymptoms = {}
results = []


def getDiseases(diseases_for_symptoms):
    diseases = []
    for disease_for_symptom in diseases_for_symptoms:
        disease_text = disease_for_symptom.text
        if "(" in disease_text:
            disease_text = disease_text.split("(")[0]
        if ":" in disease_text:
            disease_text = disease_text.split(":")[0]
        if not "?" in disease_text and not "When" in disease_text:
            diseases.append(disease_text)
    return diseases


def getDiseasesForSymptom(symptom_soup):
    diseases_for_symptom = []
    diseases = symptom_soup.find('div', class_="indexDCList")
    if not diseases:
        diseases = symptom_soup.find('ul', class_="condlist")
    if diseases:
        diseases_for_symptom = diseases.find_all('h2', itemprop="alternativeHeadline")
    return diseases_for_symptom


def getDiseasesForSymptomsLink(symptoms, diseases_with_symptoms):
    for symptom in symptoms:
        symptom_links = symptom.find_all('a')
        for symptomLink in symptom_links:
            symptom = symptomLink.text
            if not "Symptoms" in symptom and not "Signs" in symptom:
                symptom_page = requests.get(symptomLink['href'])
                symptom_soup = BeautifulSoup(symptom_page.content, 'html.parser')
                diseases_for_symptom = getDiseasesForSymptom(symptom_soup)
                if diseases_for_symptom:
                    diseases = getDiseases(diseases_for_symptom)
                    for disease in diseases:
                        if disease in diseases_with_symptoms:
                            symptoms_list = diseases_with_symptoms[disease]
                            symptoms_list.append(symptom)
                        else:
                            diseases_with_symptoms[disease] = [symptom]

def getData(link):
    diseases_with_symptoms = {}
    realLink = link.find('a')['href']
    symptom_page = requests.get(paper_link + realLink)
    symptomps_soup = BeautifulSoup(symptom_page.content, 'html.parser')
    page_symptoms = symptomps_soup.find('div', class_="AZ_results")
    symptoms = page_symptoms.find_all('li')
    getDiseasesForSymptomsLink(symptoms, diseases_with_symptoms)
    return diseases_with_symptoms

def multiprocessing_func(x, diseases_list):
    diseases_list.append(getData(x))

if __name__ == '__main__':
    paper_link_aux = 'https://www.medicinenet.com/symptoms_and_signs/alpha_a.htm'
    page = requests.get(paper_link_aux)
    soup = BeautifulSoup(page.content, 'html.parser')
    total_symptoms_div = soup.find_all('div', id="A_Z")[0]
    total_symptoms_link = total_symptoms_div.find_all('li')
    processes = []
    manager = multiprocessing.Manager()
    results_list = manager.list()

    for link in total_symptoms_link:
        print(f"Ahora empieza en link {link}")
        p = multiprocessing.Process(target=multiprocessing_func, args=(link, results_list))
        processes.append(p)
        p.start()

    for proc in processes:
        proc.join()
        print("Ahora ha acabado 1 link")

    d1 = {k: v for e in results_list for (k, v) in e.items()}

    print(f"Este es el diccionario resultante: \n\n {d1}")