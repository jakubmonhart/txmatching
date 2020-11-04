# IKEM Deployment

## Connect Into Machine in IKEM VPN

1. Download [Forticlient VPN](https://www.forticlient.com/downloads) to access their network. It has just Windows and OSX versions.
1. Login into IKEM network via *Forticlient VPN*, credentials should be stored in [Bitwarden](https://vault.bitwarden.com/#/). SMS verification code will be sent to you.
1. Connect to machine via SSH (credentials should be stored in [Bitwarden](https://vault.bitwarden.com/#/)).
1. Use *root* account for management, i.e., `su root`, credentials should be stored in your home directory and better in [Bitwarden](https://vault.bitwarden.com/#/) too.
1. Follow instructions in *compose* folder.