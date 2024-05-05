# MUEI - CSAI

Team: KeyWhisperers

Authors:

- Daniel Vicente Ramos (daniel.vicente.ramos@udc.es)
- Daniel Silva Iglesias (daniel.silva.iglesias@udc.es)

# Usage

In order to execute this python script, you need to execute the following commands:

## Windows

```python
# If there's no environment created
python -m venv ".venv"

# Activate the environment
".venv/Scripts/activate.bat"

# Install all the dependencies
pip install -r requirements.txt

# Run the script
python KeyWhisperers.py test/JdP_001_input test/JdP_001_dictionary test/JdP_001_hash

# Deactivate the environment
".venv/Scripts/deactivate.bat"
```
## Docker 

To be able to run this script in docker you must first build the Docker image using

```sh
docker build -t key-whisperers .
```

Then you can run the following command to crack the Virgene cypher

```sh
docker run -it --rm --name key-whisperers-running key-whisperers
```

The docker enprypoint targets by default the files for the first encrypted text but you can alter that by running something like this:
```sh
docker run -it --rm --entrypoint python key-whisperers ./KeyWhisperers.py test/your-input-file test/your-dictionary-file test/your-hash-file
```

> IMPORTANT! Remember to build the docker image again in case you included the new encrypted text after building the image. And the file must be at least in the docker build context folder or a child of it

For example:
```sh
docker run -it --rm --entrypoint python key-whisperers ./KeyWhisperers.py test/JdP_002_input test/JdP_002_dictionary test/JdP_002_hash
```

If you want to access the bash console of docker to try the commands first you can use

```sh
docker run -it --rm --name key-whisperers-running --entrypoint /bin/bash key-whisperers
```

# References

https://github.com/pushkar-15/Vigenere-Cipher-Decrypter/
https://github.com/ichantzaras/polysub-cryptanalysis/
https://youtu.be/TxClRjnRNJw?si=heD_dTB_Ks9rl-OR