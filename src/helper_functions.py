#Import libraries:
import pygame
from pygame.locals import *
import numpy as np
import pandas as pd
import random
import time


#Generate standard & oddball sounds according to parameters specified, and randomly assign them to each run:
def generate_sounds(n_beeps, n_runs, beep_duration, freq, ratio_oddball, p_id):
    dt = 1/44100
    beep_duration /= 1000
    t_simple = np.arange(dt, beep_duration, dt)
    fade = 0.01
    amplification_f = 16383
    ramp = np.linspace(0, 1, int(fade/dt))
    pad_l = 300
    sound_len = int(beep_duration/dt + pad_l - 1)
    
    s = np.zeros((len(freq), sound_len))
    for sind in range(s.shape[0]):
        sound_temp = np.sin(2*np.pi * freq[sind] * t_simple) * amplification_f
        sound_temp = np.multiply(sound_temp, np.concatenate([ramp, np.ones(len(t_simple) - 2*len(ramp)), ramp[::-1]]))
        s[sind] = np.concatenate([sound_temp, np.zeros(pad_l)])
    
    sounds = np.zeros((n_runs, n_beeps, sound_len))
    oddballs = np.zeros((n_runs, int(n_beeps * ratio_oddball)))
    try: random.seed(int(p_id))  #for reproducibility, set seed to Participant ID
    except: pass

    for r in range(n_runs):
        sounds_prep = np.zeros((n_beeps, sound_len))
        
        iind = np.sort(np.array(random.sample(range(0, n_beeps), int(n_beeps * ratio_oddball))))  #randomize oddball positions
        while ratio_oddball < 0.45 and (any(np.diff(iind) <= 1) or iind[0] < 2):               #ensure no consecutive oddballs
            iind = np.sort(np.array(random.sample(range(0, n_beeps), int(n_beeps * ratio_oddball))))
        
        sounds_prep[::] = s[0]
        sounds_prep[np.array(iind)] = s[1]  #replace the oddball sounds
        sounds[r] = sounds_prep
        
        oddballs[r][::] = iind              #keep track of oddball indexes
    
    oddballs = np.sum(np.eye(n_beeps)[oddballs.astype(int)], 1)   #one-hot representation, useful for performance assessment

    return [sounds, oddballs]
    

#Helper function to wait for user input & add a little "3, 2, 1..." animation:
def start_with_countdown(screen):
    font = pygame.font.SysFont('Consolas', 100)    
    text = 'Press SPACE to start...'.center(25)
    waiting = True
    
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: 
                waiting = False
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                print("🛑 Script interrupted by user")
                return False
        screen.fill((0, 0, 0))
        screen.blit(font.render(text, True, (80, 80, 80)), (90, 380))
        pygame.display.flip()
    
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    font = pygame.font.SysFont('Consolas', 300)    
    counter, text = 3, '3'.center(1)
    counting = True
    
    while counting:
        for e in pygame.event.get():
            if e.type == pygame.USEREVENT: 
                counter -= 1
                if counter > 0:
                    text = str(counter).center(1)
                else:
                    counting = False
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                print("🛑 Script interrupted by user")
                return False
        screen.fill((0, 0, 0))
        screen.blit(font.render(text, True, (255, 255, 255)), (680, 300))
        pygame.display.flip()
    
    return True
    

#Helper function to wait at the end of each run, until the next one can start:
def end_with_cooldown(screen, is_last_run = False, cooldown = 5):
    screen.fill((0, 0, 0))
    if is_last_run:
        font = pygame.font.SysFont('Consolas', 80)
        screen.blit(font.render('Thanks for participating :)'.center(30), True, (200, 200, 200)), (100, 380))
    else:
        font = pygame.font.SysFont('Consolas', 100)
        screen.blit(font.render('Nice job!'.center(10), True, (200, 200, 200)), (550, 380))
    pygame.display.flip()

    start_time = pygame.time.get_ticks()
    end_time = pygame.time.get_ticks() + cooldown*1000

    while start_time < end_time:
        start_time = pygame.time.get_ticks()                
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:  #cooldown can be skiped by pressing ENTER
                start_time = end_time
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                print("🛑 Script interrupted by user")
                return True
    return False
 
 
#Main application loop that will instruct the participant to conduct the oddball experiment, and output the results as a pandas dataframe:
def run_session(timings, sounds, oddballs, n_beeps, n_runs, silence_duration, start_from_run = 0):
    pygame.mixer.pre_init(44100, -16, 2, 32)   #setup mixer to avoid sound lag
    pygame.init()
    pygame.display.set_caption("Oddball Session 🕹️")
    screen = pygame.display.set_mode([1536, 864])  #set up drawing window (leave empty for fullscreen mode)
    bg = pygame.image.load("img/background.jpg")       #artsy background

    for r in range(start_from_run, n_runs):
        print("Starting run #{}! 🏁      Time: {}".format(r, time.strftime("%H:%M:%S")))
        sounds_run = np.array(sounds[r])

        playing = start_with_countdown(screen)

        last_time = time.time()
        b = 0

        while b <= n_beeps and playing:
            screen.blit(bg, (0,0))
            pygame.display.flip()
            
            if (time.time() - last_time) > (silence_duration/1000 - 0.005):  #play sound
                if b < n_beeps:
                    pygame.mixer.Sound(sounds_run[b, :].astype('int16')).play()
                    timings[r, b, 0] = pygame.time.get_ticks()/1000               #record when sound plays
                    
                last_time = time.time()
                b += 1
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    print("🛑 Script interrupted by user")
                    playing = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and b > 0:   #record when user reacts
                    timings[r, b-1, 1] = pygame.time.get_ticks()/1000 - timings[r, b-1, 0]
        
        if not playing or end_with_cooldown(screen, r == n_runs-1): break    #wait until next run can start, or press ENTER to skip

    pygame.quit()  #exit application
    
    results = pd.DataFrame("", index = ["Run " + str(i) for i in range(n_runs)], columns = range(n_beeps))  #create spreadsheet with readable results
    for i in range(start_from_run, r+1):
        for j in range(n_beeps):
            if oddballs[i, j] == 0:
                if timings[i, j, 1] == 0:
                    results.at["Run " + str(i), j] = "-"
                else:
                    results.at["Run " + str(i), j] = "Wrong keypress"
            else:
                if timings[i, j, 1] == 0:
                    results.at["Run " + str(i), j] = "Missed oddball"
                else:
                    results.at["Run " + str(i), j] = str(np.round(timings[i, j, 1], 3)) + " seconds"
    
    return results