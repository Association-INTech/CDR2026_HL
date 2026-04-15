# SSH

Remplacer par l'addresse IP de la pi (-X nécessaire pour pouvoir éxécuter la console)
```bash
   ssh -X intech@192.168.1.175 
```
 -X nécessaire pour éxecuter la console CAN

Aller dans le repo CDR2026_HL sur la pi_ 
Par exemple:
```bash
   cd cdr/CDR2026_HL
```

# Stratégie principal en 1 commande
```bash
   ./run.sh
```

# Lancement

## Setup CAN/Lidar

```bash
   ./canBus/setup_can.sh
```

Lidar
```bash
lidar/hokuyo/setup_lidar.sh
```

## Option 1 (avec venv)

Requirement: avoir config l'env sur la pi au préalable

### Setup env
```bash
   source venv/bin/activate
```

### Lancement
Stratégie principal
```bash
   python behaviour_tree/mainChasseNeige.py
```

Test qui effectue seulement un demi-tour avec un arbre de comportement
```bash
   python behaviour_tree/mainTest.py
```

Console CAN
```bash
   python canBus/CommunicationCan.py
```


## Option 2 (avec uv)

Requirement: avoir installé uv sur la pi

### Setup env
```bash
   uv sync --extra all
```

### Lancement
Stratégie principal
```bash
   uv run behaviour_tree/mainChasseNeige.py
```

Test qui effectue seulement un demi-tour avec un arbre de comportement
```bash
   uv behaviour_tree/mainTest.py
```

Console CAN
```bash
   uv run canBus/CommunicationCan.py
```
# Simulation
Après avoir installé uv:  https://docs.astral.sh/uv/getting-started/installation/
```bash
   uv run behaviour_tree/mainChasseNeige.py --sim
```

# Installation et config
TODO