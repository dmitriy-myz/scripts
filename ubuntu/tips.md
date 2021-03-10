audio noise on silent

```
options snd_hda_intel power_save=0
```

enable guc

```
options i915 enable_guc=2

```


```Section "Device"
   Identifier  "Intel Graphics"
   Driver      "intel"
   Option      "TearFree"    "true"
   VideoRam     524288
   #Option  "TripleBuffer" "true"
   #Option "AccelMethod" "uxa"
EndSection
```
