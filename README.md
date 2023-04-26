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
    - [x] Begin runninng the pump (turn on relay 0)
    - [x] Stop running the pump (turn off relay 0)
    - [x] Read data from either RH probe
    - [x] Read data from the ADC chnn 0 (solvent % - solvent probe)
    - [x] Read data from the ADC chn 2 (temp - solvent probe)
    - [ ] Boolean function to test if a flash drive is connected
    - [ ] Start/Stop humidifcation process button function
    - [ ] Start/Stop recording data function
        - [ ] Toggles a global variable RECORDING_DATA (native state = False)
    - [ ] 

# Software Setup

1. Make the launcher script executable:
    ```
    $: chmod 755 launcher.sh
    ```
2. Add a logs directory:
    ```
    $: cd
    ```
    ```
    $: mkdir logs
    ```
3. Add your Crontab
    ```
    $: sudo crontab -e
    ```
    This will bring up the crontab window, enter:
    ```
    @reboot sh /home/pi/bbt/launcher.sh >/home/pi/logs/cronlog 2>&1 
    ```
4. Reboot the system to see if it worked
    ```
    $: sudo reboot
    ```

# Shutdown Button Setup

1. Next we need to start listen_for_shutdown.py on boot. So we'll place the script in /usr/local/bin:  
    ```  
    $: mv listen-for-shutdown.py /usr/local/bin/    
    ```
    Then make it executable:  
    ```
    $: chmod +x /usr/local/bin/listen-for-shutdown.py  
    ```  
2. Place listen_for_shutdown.sh in /etc/init.d: 
    ```  
    $: sudo mv listen-for-shutdown.sh /etc/init.d/  
    ```
    Then make it executable:  
    ```
    $: sudo chmod +x /etc/init.d/listen-for-shutdown.sh  
    ```  
5. Now we'll register the script to run on boot:  
    ```  
    $: sudo update-rc.d listen-for-shutdown.sh defaults  
    ```  
6. Since the script won't be running, we'll go ahead and start it with:  
    ```  
    $: sudo /etc/init.d/listen_for_shutdown.sh start
    ```  
    or just reboot reboot with  
    ```  
    $: sudo reboot  
    ```  
