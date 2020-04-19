import os
import os
import time
import gym
import gym_donkeycar

def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

class DonkeyGymEnv(object):

    def __init__(self, sim_path, host="127.0.0.1", port=9091, headless=0, env_name="donkey-generated-track-v0", sync="asynchronous", conf={}, delay=0, cam_conf=None, start_sim=True, return_rewards=False ):
        os.environ['DONKEY_SIM_PATH'] = sim_path
        os.environ['DONKEY_SIM_PORT'] = str(port)
        os.environ['DONKEY_SIM_HEADLESS'] = str(headless)
        os.environ['DONKEY_SIM_SYNC'] = str(sync)

        self.return_rewards = return_rewards

        if sim_path != "remote" and start_sim:
            if not os.path.exists(sim_path):
                raise Exception("The path you provided for the sim does not exist.") 

            if not is_exe(sim_path):
                raise Exception("The path you provided is not an executable: " + sim_path) 

        #self.env = gym.make(env_name, exe_path=sim_path, host=host, port=port, start_sim=start_sim)
        self.env = gym.make(env_name, exe_path=sim_path, host=host, port=port)
        self.frame = self.env.reset()
        self.action = [0.0, 0.0]
        self.running = True
        self.info = { 'pos' : (0., 0., 0.)}
        self.reward = 0.0
        self.delay = float(delay)

        if "body_style" in conf:
            self.env.viewer.set_car_config(conf["body_style"], conf["body_rgb"], conf["car_name"], conf["font_size"])
            #without this small delay, we seem to miss packets
            time.sleep(0.1)

        if cam_conf is not None:
            self.env.viewer.set_cam_config(**cam_conf)
            time.sleep(0.1)

    def update(self):
        while self.running:
            self.frame, self.reward, _, self.info = self.env.step(self.action)

    def run_threaded(self, steering, throttle):
        if steering is None or throttle is None:
            steering = 0.0
            throttle = 0.0
        if self.delay > 0.0:
            time.sleep(self.delay / 1000.0)
        self.action = [steering, throttle]
        if self.return_rewards:
            return self.frame, self.reward
        else:
            return self.frame

    def shutdown(self):
        self.running = False
        time.sleep(0.2)
        self.env.close()


    
