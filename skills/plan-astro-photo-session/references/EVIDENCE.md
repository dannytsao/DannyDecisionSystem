# Astro Pilot Evidence

Checked: 2026-07-12

## Supported principles

- Taiwan CWA explains that fog forms when air cools to saturation or moisture increases, and distinguishes several mechanisms including radiation, advection and upslope fog. It generally calls horizontal visibility below 1 km fog and below 200 m dense fog. Therefore 5 km is not a universal white-wall threshold. [CWA fog overview](https://pweb.cwa.gov.tw/PopularScience/wt/wt_12.html)
- NOAA guidance likewise treats dew-point spread as one ingredient and describes different fog mechanisms. Small spread raises risk but does not prove fog at a mountain viewpoint. [NWS fog guide](https://www.weather.gov/media/zhu/ZHU_Training_Page/fog_stuff/fog_guide/fog.pdf)
- Moon impact depends on illumination, altitude, angular separation, wavelength and target. ESO observing constraints use multiple moon and sky variables rather than one illumination cutoff. [ESO observing conditions](https://www.eso.org/sci/observing/phase2/ObsConditions.PIONIER.html)
- Seestar S50's built-in dual narrow-band filter is described for light-pollution use; the manual does not establish a 50% moon-illumination trigger. [Seestar S50 manual](https://i.seestar.com/owe__prod/static/manuals/SeestarManualEN.pdf)
- Upper-air jet stream and ground wind are different evidence. Do not infer tripod vibration directly from jet speed. [Met Office jet-stream overview](https://weather.metoffice.gov.uk/learn-about/weather/types-of-weather/wind/what-is-the-jet-stream)

## Equipment facts

- DJI Mini 3 Pro maximum wind-speed resistance: 10.7 m/s, Level 5. [DJI Mini 3 Pro support](https://www.dji.com/support/product/mini-3-pro)
- DJI Avata 2 maximum wind-speed resistance: 10.7 m/s, Level 5. [DJI Avata 2 specifications](https://www.dji.com/avata-2/specs)
- DJI Mavic 2 maximum wind-speed resistance: 29–38 km/h. [DJI Mavic 2 support](https://www.dji.com/support/product/mavic-2)
- These are manufacturer maxima, not automatic Go thresholds. Include gusts, terrain, battery, return direction, pilot skill and local restrictions.
- Taiwan CAA requires checking official prohibited or restricted areas and notes that its GIS does not replace other applicable laws or the underlying official announcements. [CAA drone map guidance](https://drone.caa.gov.tw/%E6%9F%A5%E8%A9%A2/Default/Security)

## Rejected universal rules from the old GPT

| Old rule | Pilot disposition |
| --- | --- |
| Visibility under 5 km equals white wall | Reject; use observed target visibility and CWA fog definitions |
| T+24 95%, T+48 75%, T+72 50% | Reject until local calibration supports numerical caps |
| Dew-point spread under 1.5°C plus light wind guarantees fog | Keep only as a risk signal |
| Moon illumination above 50% requires a dual-band filter | Reject; use target and moon geometry plus filter purpose |
| Jet stream above 30 m/s means tripod vibration | Reject; separate seeing from ground wind and equipment stability |
| Surface wind above 10 km/h always prevents reflection | Keep only as a site-specific hypothesis |

## Calibration rule

Record predictions and actual outcomes, but promote a new local rule only after repeated cases or one high-cost event with clear causal evidence.
