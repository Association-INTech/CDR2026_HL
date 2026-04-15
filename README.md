# SSH

Remplacer par l'addresse IP de la pi (-X nécessaire pour pouvoir éxécuter la console)
```bash
   ssh -X intech@192.168.1.175 
```
Aller dans le repo CDR2026_HL sur la pi_ 
Par exemple:
```bash
   cd cdr/CDR2026_HL
```

# Script pour éxecuter stratégie principal
(Ça prend du temps c'est normal)
```bash
   ./run.sh
```

# Lancement

## Setup CAN/Lidar (À faire en premier)

```bash
   ./canBus/setup_can.sh
```

Lidar
```bash
lidar/hokuyo/setup_lidar.sh
```

## Option 1 (avec venv)

Requirement: avoir config l'env sur la pi au préalable (Deja fait)

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

Camera
```bash
   python camera/tag_aruco_scanner.py
```

## Option 2 (avec uv)

Requirement: avoir installé uv sur la pi (Deja fait)

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

Camera
```bash
   uv run camera/tag_aruco_scanner.py
```


# Simulation
Après avoir installé uv:  https://docs.astral.sh/uv/getting-started/installation/
```bash
   uv run behaviour_tree/mainChasseNeige.py --sim
```

# Installation et config
TODO