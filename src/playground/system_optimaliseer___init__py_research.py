import os


def optimaliseer_init_py(pakket_pad):
    """
    Zorgt ervoor dat er een leeg __init__.py-bestand bestaat in het opgegeven pakketpad.

    Args:
        pakket_pad: Het pad naar de map die als Python-pakket moet fungeren.
    """
    init_py_pad = os.path.join(pakket_pad, "__init__.py")

    if not os.path.exists(init_py_pad):
        try:
            open(init_py_pad, "a").close()  # Maak het bestand aan als het niet bestaat
            print(f"__init__.py aangemaakt in: {pakket_pad}")
        except Exception as e:
            print(f"Fout bij het aanmaken van __init__.py: {e}")
    else:
        print(f"__init__.py bestaat al in: {pakket_pad}")


if __name__ == "__main__":
    # Voorbeeldgebruik:  Maak een testmap en een __init__.py-bestand
    test_pakket_pad = "test_pakket"
    if not os.path.exists(test_pakket_pad):
        os.makedirs(test_pakket_pad)
    optimaliseer_init_py(test_pakket_pad)

    # Optioneel: Ruim de testmap op na afloop (niet verplicht, maar handig voor tests)
    # import shutil
    # shutil.rmtree(test_pakket_pad) # Uncomment to clean up the test dir
