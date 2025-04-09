# Spotify-Current-Song-Display
A webapp to display the current song playing from spotify

IT IS IMPARITIVE YOU FOLLOW ALL INSTRUCTIONS IN THIS READ ME.

make sure the text files and json files are set up the way you want before running the .exe file. (instructions below)

You will need api access information from https://developer.spotify.com/

Instructions on what info to put where is in the spotify_secret.txt file

MAKE SURE THAT YOU SET THAT UP PROPERLLY BECAUSE IT WILL BREAK AND NOT WORK IF YOU DO IT WRONG THE FIRST TIME
  AND MAKE SURE THAT YOU LOG IN WITH THE CORRECT SPOTIFY ACCOUNT THE FIRST TIME OR ELSE IT WILL ALSO BREAK
    (if someone knows how to fix it let me know somehow.)

Also make sure that the redirect uri in the developer portal is the same as what is in the Song_Title_Config.json file

the "deb" option in the config file is to make it show stuff for debugging in the console, but it is stuff you dont need to see normally.

the "accessible_by_other_computers_on_local_network" option is for setting wheather or not you want it to be able to be acessed by another computer on the same network

TO SEE IT:

  http://localhost:{port}/

  replace "{port}" brackets and all whith whatever port you set in the config file.

  if you have it accessible by other computers (mentioned line 20) then you will need to get the ipv4 address of the host pc and replace localhost with that ip address.

  
