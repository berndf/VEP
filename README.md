# VEP
## Citation
This is the stimulation package used in:
```
@article{ Galuba:2025,
 author	= {Galuba, Viktoria and Wolf, Theresa and Ihle, Anouk and von der
Decken, Franziska and Mülsch, Felix and Feige, Bernd and Vlachos, Andreas and
Domschke, Katharina and Normann, Claus and Vestring, Stefan},
 title	= {Development of {VEP}-based biomarkers to assess plasticity states},
 journal	= {Transl. Psychiatry},
 volume	= {15},
 pages	= {426},
 year	= {2025},
 month	= {Oct},
 keywords	= {Humans; *Evoked Potentials, Visual/physiology; Male; *Neuronal
Plasticity/physiology; Female; *Electroencephalography/methods; Adult; *Visual
Cortex/physiology; Biomarkers; Young Adult; *Long-Term
Potentiation/physiology},
 address	= {Department of Psychiatry and Psychotherapy, Medical Center,
University of Freiburg, Faculty of Medicine, University of Freiburg, Freiburg,
Germany.; German Center for Mental Health (DZPG), Berlin/Potsdam, Germany.},
 doi	= {10.1038/s41398-025-03676-x; 426},
 annote	= {Disturbances in neuroplasticity are associated with many
psychiatric and neurological disorders. Noninvasive electroencephalography
(EEG) recordings of visually evoked potentials (VEPs) are promising for
assessing plasticity in the human visual cortex, which may represent long-term
potentiation (LTP). However, the variability in stimulation parameters limits
the comparability and identification of optimal plasticity-inducing protocols.
In this study, we systematically compared four VEP modulation protocols-low-
frequency, repeated low-frequency, high-frequency, and theta-pulse stimulation-
and assessed their effects on visual cortical plasticity. We analyzed 152 EEG
recordings, where VEPs were evoked via a checkerboard reversal stimulus before
and after low-frequency, repeated low-frequency, high-frequency, and theta-
pulse stimulation. Changes in VEP amplitudes were measured from baseline to 2-
28 min postmodulation. Low-frequency stimulation produced transient changes
in plasticity, peaking at 2 min but dissipating within 12 min. Repeated
low-frequency stimulation induced more sustained changes in plasticity,
persisting for up to 22 min. High-frequency stimulation induced sharp but
brief increases in plasticity indices, whereas theta-pulse stimulation was
associated with moderate but prolonged changes in plasticity, lasting up to
28 min. These findings highlight the crucial influence of stimulation
parameters on short- and long-term synaptic plasticity indices. Depending on
the objective, a suitable induction protocol can be selected to optimize the
desired effects, such as increasing sensitivity to drug effects or targeting
longer-lasting plasticity outcomes. Optimized VEP paradigms have strong
translational potential for assessing neuroplasticity deficits in individuals
with psychiatric and neurodegenerative disorders, paving the way for the
development of new biomarkers and therapeutic strategies.}
}
```

## Requirements

python with package [expyriment](https://expyriment.org/)

For the GUI(s) VEP.py and OptiVEP.py, you'll additionally need GTK3 and
pygobject.

## Usage

The GUIs enable entering the subject code and (in case of OptiVEP)
managing the different measurement time points with randomization of the order
of conditions. They then just start the actual stimulation run (consisting of VEP
and modulation blocks) by starting checkerboard.py with corresponding parameters.

```
checkerboard.py [subject [variant [grating_{horizontal|vertical}]]]
```
Here, subject is the subject code (eg K011), variant is one of:
```
default demo ceiling pulse theta Kirk Mixed11 Mixed21 Mixed12 Mixed22 NormannOhne KirkOhne Kirk10min2Hz
```
"default" (also used if no variant is given) is the 10-min-2-rps checkerboard
reversal paradigm of [Normann et al. (2007)](https://doi.org/10.1016/j.biopsych.2006.10.006).

"kirk" refers to the grating stimulation derived from [https://github.com/RachaelSumner/VisualLTP](https://github.com/RachaelSumner/VisualLTP).

CB.py is the support module defining the building blocks of all paradigm variants.
