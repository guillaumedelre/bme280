# Audit - BME280 Sensor Project

**Scope:** `bme280.py`, `sensor-api.py` | **Files:** 2 | **Findings:** 2 ❌  3 ⚠️  4 💡

---

## TL;DR

Projet fonctionnel mais en Python 2 avec des credentials en clair. La priorité absolue est la migration Python 3 et la sécurisation de la config. Une fois ça fait, le code est structurellement sain et prêt pour un pipeline CI.

---

## Findings

❌ **Credentials MQTT hardcodés dans le source** - `sensor-api.py:9-14`
  Mot de passe, IP du broker, username directement dans le code versionné.
  **Fix:** variables d'environnement via `os.environ.get()` + fichier `.env` exclu du git.

```python
# Avant
password = 'chi6pa9tiom3chahhohB7sienicae2aimimeefei4queol7eesuthohcai6maiph'
broker_host = '192.168.86.35'

# Après
import os
password    = os.environ.get('MQTT_PASSWORD', '')
broker_host = os.environ.get('MQTT_BROKER_HOST', 'localhost')
```

❌ **Python 2** - `bme280.py:208-215`
  Syntaxe `print "..."` sans parenthèses, EOL depuis janvier 2020. Plus de patches de sécurité, incompatible avec les outils modernes (pytest, mypy, etc.).
  **Fix:** migration vers Python 3 + remplacement de `smbus` par `smbus2`.

```python
# Avant
print "Temperature :", temperature, "C"

# Après
print(f"Temperature : {temperature:.2f} °C")
```

⚠️ **Aucune gestion d'erreur** - `sensor-api.py`, `bme280.py`
  Si le capteur est absent, l'I2C plante ou le broker MQTT est injoignable, l'API retourne une 500 brute sans message utile.
  **Fix:** try/except avec réponse JSON structurée et code HTTP approprié.

```python
@app.route('/bme280')
def bme280_action():
    try:
        return jsonify(bme280.sensor())
    except OSError as e:
        return jsonify({'error': 'Sensor unavailable', 'detail': str(e)}), 503
```

⚠️ **Flask en mode debug en production** - `sensor-api.py:43`
  `debug=True` active le debugger Werkzeug interactif, exécutable à distance sur le réseau.
  **Fix:** `debug=False` ou piloter via variable d'environnement `FLASK_DEBUG`.

⚠️ **`bme280.pyc` tracké dans git**
  Bytecode compilé qui ne devrait pas être versionné. Il peut diverger silencieusement de la source.
  **Fix:** ajouter `.gitignore` avec `*.pyc` et `__pycache__/`.

💡 **Pas de `requirements.txt`** - dépendances implicites non documentées
  `smbus2`, `flask`, `paho-mqtt` doivent être devinées à la lecture du code.
  **Fix:** `requirements.txt` minimal avec les versions fixées.

💡 **Adresse I2C hardcodée à 0x77** - `bme280.py:28`
  Le BME280 supporte aussi l'adresse 0x76 (selon câblage SDO). Rendre configurable couvre les deux variantes.

💡 **Bus SMBus instancié au niveau module** - `bme280.py:31`
  `bus = smbus.SMBus(1)` s'exécute à l'import, ce qui fait crasher tout test unitaire sur une machine sans hardware I2C.
  **Fix:** instancier le bus dans les fonctions qui en ont besoin, ou l'injecter en paramètre.

💡 **`feature/v2` non mergée + commit "try POO way" orphelin**
  Code potentiellement utile qui dort dans une branche non intégrée.

---

## Roadmap modernisation

### 1. Python 3 + dépendances propres

- Remplacer `smbus` par `smbus2` (compatible Python 3, même API)
- Réécrire `bme280.py` en Python 3 avec type hints
- Créer `requirements.txt`

```
smbus2==0.4.3
flask==3.1.0
paho-mqtt==2.1.0
python-dotenv==1.0.1
```

### 2. Configuration externalisée

Créer `.env.example` (versionné) et `.env` (ignoré) :

```ini
# .env.example
MQTT_BROKER_HOST=192.168.1.x
MQTT_USERNAME=homeassistant
MQTT_PASSWORD=
MQTT_CLIENT_ID=rpi-bme280
BME280_I2C_ADDRESS=0x77
BME280_I2C_BUS=1
FLASK_PORT=5000
FLASK_DEBUG=false
```

### 3. Gestion d'erreurs et HTTP sémantique

| Cas | Status actuel | Status cible |
|-----|--------------|--------------|
| Capteur absent | 500 (crash) | 503 Service Unavailable |
| Lecture I2C timeout | 500 (crash) | 503 + retry header |
| MQTT broker injoignable | 500 (crash) | 502 Bad Gateway |
| Succès publish | 200 `{}` | 200 `{"published": true, "topics": [...]}` |

### 4. Qualité de code

- Type hints sur toutes les fonctions publiques
- Dataclass ou TypedDict pour la structure sensor
- `bus` instancié dans les fonctions (testabilité)
- `snake_case` cohérent (renommer `sensor-api.py` en `sensor_api.py`)

### 5. Tests unitaires

Le projet est très bien adapté aux tests car le hardware est isolable par mock :

```python
# tests/test_bme280.py
from unittest.mock import patch, MagicMock

def test_sensor_returns_expected_structure():
    mock_bus = MagicMock()
    mock_bus.read_i2c_block_data.return_value = [0] * 24
    with patch('bme280.smbus2.SMBus', return_value=mock_bus):
        result = bme280.sensor()
        assert 'data' in result
        assert 'temperature' in result['data']

# tests/test_api.py
def test_bme280_endpoint(client, mock_sensor):
    resp = client.get('/bme280')
    assert resp.status_code == 200
    assert resp.json['name'] == 'bme280'

def test_sensor_unavailable_returns_503(client):
    with patch('bme280.sensor', side_effect=OSError('I2C error')):
        resp = client.get('/bme280')
        assert resp.status_code == 503
```

### 6. GitHub Actions CI

Ce que la pipeline peut valider sans hardware réel :

| Job | Outil | Ce que ça couvre |
|-----|-------|-----------------|
| Lint | `flake8` | Style, erreurs évidentes |
| Types | `mypy` | Cohérence des type hints |
| Tests | `pytest` + mocks | Logique métier et routes Flask |
| Sécurité | `pip-audit` | CVE dans les dépendances |

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: flake8 bme280.py sensor_api.py
      - run: mypy bme280.py sensor_api.py
      - run: pytest tests/ -v --tb=short
      - run: pip-audit
```

### 7. Documentation

- README complet avec badges CI, exemples curl, schéma d'architecture
- Exemples d'intégration Home Assistant (MQTT discovery)
- Docstrings sur les fonctions publiques
- Schéma de câblage I2C Raspberry Pi / BME280

---

## Exemples d'utilisation cibles

### CLI

```bash
# Lecture directe
python bme280.py
# Temperature : 21.55 °C  |  Pressure : 1005.16 hPa  |  Humidity : 44.57 %RH

# Avec adresse I2C alternative
BME280_I2C_ADDRESS=0x76 python bme280.py
```

### API HTTP

```bash
# Démarrer l'API
python sensor_api.py

# Lire les données capteur
curl http://rpi.local:5000/bme280 | python -m json.tool

# Publier vers MQTT
curl -X POST http://rpi.local:5000/bme280/publish
# {"published": true, "topics": ["sensor/bme280_temperature", ...]}

# Healthcheck
curl http://rpi.local:5000/health
# {"status": "ok", "sensor": "connected"}
```

### Intégration Home Assistant (MQTT Discovery)

```yaml
# configuration.yaml
mqtt:
  sensor:
    - name: "BME280 Temperature"
      state_topic: "sensor/bme280_temperature"
      unit_of_measurement: "°C"
      device_class: temperature
    - name: "BME280 Humidity"
      state_topic: "sensor/bme280_humidity"
      unit_of_measurement: "%"
      device_class: humidity
    - name: "BME280 Pressure"
      state_topic: "sensor/bme280_pressure"
      unit_of_measurement: "hPa"
      device_class: atmospheric_pressure
```

### Cron (après migration)

```bash
# Publier toutes les minutes
* * * * * curl -s -X POST http://localhost:5000/bme280/publish >> /var/log/bme280.log 2>&1
```

---

## Résumé

| Priorité | Action | Effort |
|----------|--------|--------|
| ❌ Immédiat | Retirer les credentials du code | 30 min |
| ❌ Court terme | Migration Python 3 | 2h |
| ⚠️ Court terme | Gestion d'erreurs + `.gitignore` | 1h |
| 💡 Moyen terme | Tests unitaires + CI GitHub Actions | 3h |
| 💡 Moyen terme | Docker + `.env.example` | 1h |
| 💡 Long terme | README complet + exemples | 2h |

**Verdict:** Le coeur algorithmique (calibration BME280) est correct et bien isolable. La dette principale est Python 2 + sécurité. Une fois ces deux points traités, le projet peut servir de base solide avec pipeline CI complète.
