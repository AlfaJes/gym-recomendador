# 🏋️ Gym Recomendador

App para recomendar ejercicios de entrenamiento de gimnasio.
Selecciona un grupo muscular y obtén los mejores ejercicios con series, repeticiones y descripción.

## 🚀 Cómo usarla (Android)

### Opción 1: PWA (recomendada — no necesita instalación)

1. Abre `pwa/index.html` en Chrome en tu celular
2. Toca el menú ⋮ → **Agregar a pantalla de inicio**
3. Se comportará como una app nativa

### Opción 2: Servidor local

```bash
cd pwa && python3 -m http.server 8080
# Abre http://IP:8080 en tu celular
```

## 📋 Funcionalidades

- 7 grupos musculares: Pecho, Espalda, Piernas, Hombros, Bíceps, Tríceps, Abdominales
- 35+ ejercicios con series, reps y descripción
- 4 rutinas predefinidas (Push/Pull/Legs/Full Body)
- Offline-ready (service worker)
- Modo oscuro
- Diseño mobile-first

## 🛠️ Para desarrollar (APK nativo)

Para generar un APK real de Android:

```bash
# Opción A: Expo (recomendado para React Native)
npx create-expo-app . --template blank
npm install
npx expo start
# Escanea el QR con Expo Go en tu celular

# Opción B: EAS Build (APK en la nube)
npm install -g eas-cli
eas login
eas build --platform android --profile preview
```

## 📂 Estructura

```
gym-recomendador/
├── pwa/                    # App web progresiva (funciona ya)
│   ├── index.html          # App principal
│   ├── manifest.json       # Config PWA
│   ├── sw.js               # Service Worker (offline)
│   └── icons/              # Iconos de la app
├── generate-icons.py       # Generador de iconos
└── README.md
```
