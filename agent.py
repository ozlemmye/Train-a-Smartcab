import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # Initialize any additional variables here
        self.Q = {}
        self.R = {}
        self.policy = {}
        self.reward_list = []
        
        self.x = 0.1
        self.x_list = []
        self.epsilon = 0.8
        self.alpha = 0.5
        self.gamma = 0.2
        

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # Prepare for a new trip; reset any variables here, if required
        deadline = self.env.get_deadline(self)
        print deadline
        self.state = None
        self.action = None
        self.reward = None

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        location = self.env.agent_states[self]['location']
        heading = self.env.agent_states[self]['heading']
        destination = self.planner.destination
        print location, heading, destination

        # Update state
        next_state = (inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'], self.next_waypoint)
        print ('next_state: ', next_state)   
             
        # Select action according to your policy
       
        #action = None
        print '----------------'
        #action_list = [None, 'forward', 'left', 'right']
        #self.random_action = random.choice(action_list)
        # 1) For random actions:
        #self.Q_action = self.random_action
        # 2) For actions with epsilon and decaying epsilon:
        self.Q_action = self.QAction(next_state) 
        # 3) For actions without epsilon
        #self.Q_action = self.QActionGreedy(next_state)
        
        # Execute action and get reward
        next_reward = self.env.act(self, self.Q_action)
        
        # Make Q value table:
        self.makeQ(self.state,self.action,self.reward, next_state)
        
        
        self.state = next_state
        self.action = self.Q_action
        self.reward = next_reward

        # Learn policy based on state, action, reward
        
        self.reward_list.append(next_reward)
        print ('self.reward_list: ', self.reward_list)
        sum = 0
        num_r = []
        for i in range(len(self.reward_list)):
            sum += self.reward_list[i] 
            num_r.append(i)
        print ('number of step: ', len(num_r), 'sum: ', sum)
        
        self.policy [next_state] =self.Q_action
        #print ('policy: ', self.policy)

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, self.Q_action, next_reward)  # [debug]
        # For actions with decaying epsilon, use the below code
        self.x += 0.05
        self.epsilon = 1.0 / (1.0 + self.x)
        self.x_list.append(self.x)
        
        
    def makeQ (self, state, action, reward, next_state):          
        self.possibleActions =  [None, 'forward', 'left', 'right'] 
        
        if state != None:
            next_Q = [self.Q.get ((next_state, actions),0.0) for actions in self.possibleActions]
            print ('next_Q :', max(next_Q), next_Q)        
            self.Q[state, action] = self.Q.get ((state, action), 0.0) + self.alpha * (reward + self.gamma * (max(next_Q)) - self.Q.get((state, action), 0.0))
            #print ('self.Q_1 :', self.Q)
    
                       
    def QActionGreedy (self, state):  
        self.possibleActions =  [None, 'forward', 'left', 'right']

        best_Q = [self.Q.get ((state, actions),0.0) for actions in self.possibleActions]
        print ('best_Q :', max(best_Q), best_Q)
        count_best_Q = best_Q.count(max(best_Q))
        print ('count_best_Q1: ', count_best_Q)
        
        if count_best_Q == 1:
            for state_action, rewards in self.Q.iteritems():
                if rewards == max(best_Q) and state_action[0] == state:
                    best_action = state_action[1]
                    print ('best action1_1 : ', best_action) 
                    return best_action 
                
        elif count_best_Q == 2 or count_best_Q == 3:
            ii=[]
            for i in range(len(best_Q)):
                best_Q[i] == max(best_Q)
                ii.append(i)
            random_i = random.choice(ii)

            for state_action, rewards in self.Q.iteritems():
                if rewards == best_Q[random_i] and state_action[0] == state:
                    best_action = state_action[1]
                    print ('best action1_23 : ', best_action)                    
                    return best_action           
    
        elif count_best_Q == 4:
            best_action = random.choice(self.possibleActions)
            print ('best action1_4 : ', best_action)
            return best_action
        
    def QAction (self, state):  
        self.possibleActions =  [None, 'forward', 'left', 'right']
        rand = random.random() 
        print ('----',rand )
        print ('epsilon: ', self.epsilon)
        if rand < self.epsilon:
            action = random.choice([None, 'forward', 'right', 'left'])
            #action = self.next_waypoint
            print ('epsilon action: ', action)
            return action
        else:
            best_Q = [self.Q.get ((state, actions),0.0) for actions in self.possibleActions]
            print ('best_Q :', max(best_Q), best_Q)
            count_best_Q = best_Q.count(max(best_Q))
            #print ('count_best_Q: ', count_best_Q)
        
            if count_best_Q == 1:
                for i in range(len(best_Q)):
                    if best_Q[i] == max(best_Q):
                        best_action = self.possibleActions[i]    
                        print ('best action1_1 : ', best_action) 
                        return best_action 
                        
                    
            elif count_best_Q == 2 or count_best_Q == 3:
                ii=[]
                for i in range(len(best_Q)):
                    if best_Q[i] == max(best_Q):
                        ii.append(i)
                random_i = random.choice(ii)

                for state_action, rewards in self.Q.iteritems():
                    if rewards == best_Q[random_i] and state_action[0] == state:
                        best_action = state_action[1]
                        #s = sa[0]
                        print ('best action1_23 : ', best_action)                   
                        return best_action           
        
            elif count_best_Q == 4:
                best_action = random.choice(self.possibleActions)
                print ('best action1_4 : ', best_action)
                return best_action
        

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=1.0)  # reduce update_delay to speed up simulation
    sim.run(n_trials=10)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
