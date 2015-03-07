#Bishop
______

## About

Bishop, after [Washington Bishop](http://en.wikipedia.org/wiki/Washington_Irving_Bishop), is a cognitive model of [Theory of mind](http://en.wikipedia.org/wiki/Theory_of_mind).

## Install and uninstall

	python setup.py install
	pip uninstall Bishop

## Running Bishop

#### Simulate agents traveling in an existing map

	import Bishop	
	Observer = Bishop.LoadEnvironment("Tatik_T1")
	Observer.SimulateAgents(StartingCoordinates=[6,6],Samples=100,HumanReadable=True)

To see a list of available maps just type

	import Bishop	
	Bishop.ShowAvailableMaps()

#### Cost-reward inference given observable actions

	import Bishop
	Observer = Bishop.LoadEnvironment("Tatik_T1")
	ObservedPath = Observer.GetActionList(['L','L','U'])
	Res = Observer.InferAgent(StartingCoordinates=[6,6], ActionSequence=ObservedPath, Samples=100, Softmax=True)

The result is a __PosteriorContainer__ object. Here are some things you can do with the output

	Res.Summary # Human-readable summary
	Res.AnalyzeConvergence() # Visually check if sampling converged
	Res.PlotCostPosterior()
	Res.PlotRewardPosterior()
	Res.Summary(Human=False) # prints compressed summary for easier analysis
	Res.SaveSamples("MyResults")

You can reload the samples and the observer model later with

	Res = Bishop.LoadSamples("MyResults.p")
	Observer = Bishop.LoadObserver(Res)

## Creating a new map

### Through configuration files

A map consists of two files: An ASCII description, and a .ini configuration file.

ASCII files begin with a map drawing, with each terrain type indicated numerically. After a line break, each terrain name is specified in a single line

	000
	111
	000
	
	Jungle
	Water

specifies a 3x3 map where the top and bottom row are "Jungle" and the middle row is "Water."

The second file, MapName.ini, specifies the location of the targets, the ASCII file to load, as well as other parameters. See the Maps folder for an example.

### Inside python

##### Map skeleton

To generate a simple grid-world with one terrain start with

	MyMap = Bishop.Map()
	MyMap.BuildGridWorld(5,3,Diagonal=True)

This creates a 5 by 3 map that can be navigated diagonally. Terrain type is stored in MyMap.StateTypes. The first terrain has by default a value of 0. New terrains are added through squares:

	MyMap.InsertSquare(2, 1, 2, 3, 1):

added a 2x3 square with the top-left corner positioned on (2,1). Both coordinates begin in 1 and the y-axis is counted from top to bottom. The last argument (1) gives the terrain code. Inserting overlapping squares always rewrites past terrain. You can then add terrain names

	MyMap.AddStateNames(["Water","Jungle"])

To see what your map looks like type

	MyMap.PrintMap()

##### Adding targets

SOON

##### Saving the map

SOON

##### Using the map

Once you have a map, you need to create an agent, and use both to create an observer

	MyAgent = Bishop.Agent(MyMap, CostParam, RewardParam)
	Observer = Bishop.Observer(MyMap, MyAgent)

## How it works

Bishop does bayesian inference over optimal planners to infer the cost and rewards underlying an agent's actions. It then uses the posterior distribution of costs and rewards to predict how the agent will navigate.

## Details

Bishop has six classes. You can see what each class is saving by calling the Display() method on an object.

__Observer__ objects are rational observers. They require a Map and an Agent object (see below) and have three main methods:

* **ComputeLikelihood:** Computes the likelihood that the agent would take a given sequence of actions
* **SimulateAgent:** Simulates the agent from a given starting point
* **InferAgent:** Infers the agents costs and rewards given a sequence of observable actions

See Example folder for examples on how to use these methods.

__PosteriorContainer__ objects save cost and reward samples along with their likelihoods. They store some additional information and have methods for deriving meaningful results from the samples.

__Planner__ objects contain a Markov Decision Process and supporting methods for modifying the MDP structures.

__Map__ objects contained a map's description for the agent and the observer to use. It's main method is BuildGridWorld() to generate simple 2-dimensional grid worlds.

__Agent__ objects contain agent information.

__MDP__ objects store Markov Decision Processes along with exact planning algorithms and supporting methods.