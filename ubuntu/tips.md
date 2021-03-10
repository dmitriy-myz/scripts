audio noise on silent

```
options snd_hda_intel power_save=0
```

enable guc

```
options i915 enable_guc=2

```


```
Section "Device"
   Identifier  "Intel Graphics"
   Driver      "intel"
   Option      "TearFree"    "true"
   VideoRam     524288
   #Option  "TripleBuffer" "true"
   #Option "AccelMethod" "uxa"
EndSection

Section "Module"
    Load           "dbe"
    Load           "extmod"
    Load           "type1"
    Load           "freetype"
    Load           "glx"
EndSection

Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "GeForce GTX 1070"
    Option         "nvidiaXineramaInfoOrder" "DFP-4"
    Option         "metamodes" "HDMI-0: nvidia-auto-select +0+0 {ForceCompositionPipeline=On}, DP-2: nvidia-auto-select +1920+0 {ForceCompositionPipeline=On}"
EndSection

```
