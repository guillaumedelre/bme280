# CLAUDE.md - BME280 Sensor Project

## Contexte du projet

Driver Python pour le capteur environnemental Bosch BME280 (température, pression, humidité) sur Raspberry Pi, exposé via une API HTTP Flask et une publication MQTT vers Home Assistant.

**Matériel cible:** Raspberry Pi (Rev 2+, bus I2C n°1) + capteur Waveshare BME280 (SKU 15231)
**Adresse I2C par défaut:** 0x77 (alternatif 0x76 selon câblage SDO)

---

## Architecture

```
bme280.py          Driver bas niveau I2C + calculs de calibration (datasheet Bosch)
sensor_api.py      API Flask HTTP + publication MQTT vers Home Assistant
```

Le driver lit les registres EEPROM du BME280, applique les algorithmes de compensation du datasheet officiel (page 22+), et retourne température/pression/humidité calibrées.

---

## Etat actuel du code

**Attention:** le code est en Python 2. Voir `AUDIT.md` pour la roadmap de modernisation complète.

Dépendances implicites (pas de requirements.txt) :
- `smbus` (Python 2) - à remplacer par `smbus2` lors de la migration Python 3
- `flask`
- `paho-mqtt`

---

## Contraintes hardware

Le code `bme280.py` ne peut pas tourner sans un vrai bus I2C. Sur une machine de dev (CI, laptop), **toujours mocker `smbus`** :

```python
from unittest.mock import patch, MagicMock

mock_bus = MagicMock()
mock_bus.read_i2c_block_data.return_value = [0] * 24
with patch('bme280.smbus.SMBus', return_value=mock_bus):
    # test ici
```

Le `bus = smbus.SMBus(1)` est instancié au niveau module dans l'état actuel, ce qui fait crasher l'import sans hardware. Lors de la refonte, il faut déplacer cette instanciation dans les fonctions.

---

## Algorithmes critiques

Les fonctions de compensation dans `readBME280All()` sont tirées directement du datasheet Bosch (Appendix). **Ne pas modifier sans vérifier contre la spec officielle.** Les constantes magiques (32768, 524288, 67108864...) sont des puissances de 2 issues du datasheet, pas des valeurs arbitraires.

---

## Configuration sensible

`sensor-api.py` contient actuellement des credentials MQTT hardcodés. Ne pas les modifier directement dans le source, la cible est de les externaliser en variables d'environnement. Voir `AUDIT.md` pour le plan.

Variables d'environnement cibles (après migration) :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `MQTT_BROKER_HOST` | `localhost` | IP ou hostname du broker |
| `MQTT_USERNAME` | - | Username MQTT |
| `MQTT_PASSWORD` | - | Password MQTT |
| `MQTT_CLIENT_ID` | `rpi-bme280` | Client ID MQTT |
| `BME280_I2C_ADDRESS` | `0x77` | Adresse I2C du capteur |
| `BME280_I2C_BUS` | `1` | Numéro de bus I2C |
| `FLASK_PORT` | `5000` | Port HTTP |

---

## Lancer le projet

```bash
# CLI directe (sur le Pi uniquement)
python bme280.py

# API HTTP (sur le Pi uniquement)
python sensor-api.py
# Écoute sur 0.0.0.0:5000
```

---

## Branches

| Branche | Etat |
|---------|------|
| `develop` | Branche principale active |
| `master` | Remote uniquement |
| `feature/v2` | Remote non mergée - tentative POO abandonnée |

---

## Roadmap

Le détail complet est dans `AUDIT.md`. Les grandes étapes :

1. Externaliser les credentials (sécurité, immédiat)
2. Migration Python 3 + `smbus2`
3. `requirements.txt` + `.gitignore`
4. Gestion d'erreurs dans l'API
5. Tests unitaires avec mocks hardware
6. Pipeline GitHub Actions CI

---

## Tests

Pas de tests actuellement. La cible est `pytest` avec mocks smbus et Flask test client. Voir la section "Tests unitaires" dans `AUDIT.md` pour les exemples.

Structure cible :

```
tests/
├── test_bme280.py      # Calibration, parsing registres
└── test_api.py         # Routes Flask, gestion d'erreurs
```
