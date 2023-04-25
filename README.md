# MSD_14853
Multi-Disciplinary Senior Design - Team #14853 (Advanced Polymer Development Equipment)

# Purpose
The Advanced Polymer  Development Equipment software drives a Raspberry Pi driven system including two i2c Relative Humidity/Temperature SHT30 Probes, one analog solvent sensor (run through an MCP3008 ADC chip), and a Pi Docker relay HAT board (also using an i2c serial interface). Additionally, the software runs a GUI on a touch-enable XXXxXXX screen.

# Progress
- [ ] GUI Frontend
- System Idle
    - [ ] Display Entry Humidity
    - [ ] Display Exit Humidity
    - [ ] Display Running Status
- System Running
    - [ ] Display Start Humidity
    - [ ] Display Current Humidity (enxit humidity)
- User Interface
    - [ ] Export to .csv
        - [ ] Check if a usb drive is connected
        - [ ] Checks if there is recorded data
    - [ ] Display if there is recorded data
- [ ] GUI Backend
    - [ ] Begin runninng the pump (turn on relay 0)
    - [ ] Read data from either RH probe
    - [ ] Read data from the ADC chnn 0 (solvent % - solvent probe)
    - [ ] Read data from the ADC chn 2 (temp - solvent probe)

# Use
