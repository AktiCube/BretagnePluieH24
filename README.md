# BretagnePluieH24

[@bretagne_pluie_h24](https://instagram.com/bretagne_pluie_h24) est un compte Instagram qui poste une publication dès qu'il détecte de la pluie en Bretagne sur 10 villes aléatoires de la région toutes les minutes.

[@bretagne_pluie_h24](https://instagram.com/bretagne_pluie_h24) is an Instagram account that posts a publication as soon as it detects rain in Brittany on 10 random cities in the region every minute.

## How to use

First, use Python 3.11 and install the requirements:

```bash
pip install -r requirements.txt
```

Then, you need to rename the `.env.example` file to `.env` and fill it with your own credentials.

Before running the main bot, you need to run the `generator.py` file to generate the images for every Brittany's cities.

```bash
python generator.py
```

Finally, you can run the main bot:

```bash
python main.py
```

On my side, I use my personal VPS to run the bot 24/7 with a cron job and a service.

The following service is located in `/etc/systemd/system/bretagnepluieh24.service` :
```service
[Unit]
Description=Bretagne-Pluie-H24 Bot
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=/root/BretagnePluieH24/
ExecStart=python3.11 main.py

[Install]
WantedBy=multi-user.target
```

This service is started every 30 minutes with the following cron job :
```cron
*/30 * * * * cd /root/BretagnePluieH24/ && git pull && /usr/bin/systemctl start bretagnepluieh24
```
