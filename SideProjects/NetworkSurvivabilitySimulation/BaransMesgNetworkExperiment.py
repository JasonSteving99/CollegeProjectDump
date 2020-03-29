"""
	This script runs the Monte Carlo simulation that Paul Baran
	refers to in his famous paper, 'On Distributed Communication
	Networks'. What he showed through this simulation was that 
	a distributed, dynamically routed network with even modest 
	levels of link redundancy could be robust in the face of 
	dramatic failures of internal nodes during an attack on the 
	nation's communications systems.

	Author: Jason Steving
	Original Date  : 8/26/15
        Last Updated   : 3/28/20
"""

class Node:
  def __init__(self, destroyed=False):
    # self.neighbors = []
    self.neighbors = {} # Dictionary of Neighbor Node -> "Reachable" bool.
    self.destroyed = destroyed

  def destroy(self):
    self.destroyed = True
		# break the link connecting this node to its neighbors
		# for neighbor in self.neighbors[:]:
    for neighbor in self.neighbors.keys():
      self.removeLink(neighbor)

  def isDestroyed(self):
		return self.destroyed

  def isAlive(self):
    return not self.destroyed

  def addLink(self, neighbor):
    # self.neighbors.append(neighbor)
    self.neighbors[neighbor] = True # Initialize a "Reachable" link to the given Neighbor.

  def removeLink(self, neighbor):
    # The link is bidirectional, remove it in both directions.
    # self.neighbors.remove(neighbor)
    # neighbor.neighbors.remove(self)
    self.neighbors[neighbor] = False # Mark the neighbor-link as "Unreachable".
    neighbor.neighbors[self] = False
        
  def getReachableNeighbors(self, reachable = True):
    return map(
      # Return only the neighbor node.
      lambda t: t[0],
        filter(
          # Filter for non-destroyed links.
          lambda neighbor_link: neighbor_link[1] == reachable,
          self.neighbors.items()
        )
      )


def build_node_array(dimension = 10, redundancyLevel = 3, quiet = False):
  if dimension < 2:
    raise Exception('Dimension not large enough to create a grid.')

	# first just build up all nodes
  node_array = [[Node() for _ in xrange(dimension)] for _ in xrange(dimension)]

  # now create the links between the nodes
  if redundancyLevel == 1:
    for row in xrange(dimension):
      for col in xrange(dimension):
        curr_node = node_array[row][col]
        # Add link to node on left
        if not (row == col == 0):
          curr_node.addLink(node_array[row if col > 0 else row - 1][col - 1 if col > 0 else dimension - 1])
          # Add link to node on right
        if not (row == col == dimension - 1):
          curr_node.addLink(node_array[row if col < dimension - 1 else row + 1][(col + 1) % dimension])
  elif redundancyLevel == 2:
    if not quiet:
      print '<--------------->'
      print 'Redundancy Level = 2'
      print '<--------------->'
      print '          |'
      print 'Links:  --*--'
      print '          |'
      print '<--------------->'
    for row in xrange(dimension):
      for column in xrange(dimension):
        node = node_array[row][column]
        for i in xrange(row - 1, row + 2):
          for j in xrange(column - 1, column + 2):
            # do not establish link to self, nodes out of bounds, or nodes
            # that would raise redundancy level
            if row == i and column == j:
              continue
            if i < 0 or i >= dimension or j < 0 or j >= dimension:
              continue
            if (i, j) == (row - 1, column + 1):
              continue
            if (i, j) == (row - 1, column - 1):
	            continue
            if (i, j) == (row + 1, column - 1):
	            continue
            if (i, j) == (row + 1, column + 1):
	            continue
            node.addLink(node_array[i][j])
  elif redundancyLevel == 3:
    if not quiet:
		  print '<--------------->'
		  print 'Redundancy Level = 3'
		  print '<--------------->'
		  print '         \|'
		  print 'Links:  --*--'
		  print '          |\\'
		  print '<--------------->'
    for row in xrange(dimension):
      for column in xrange(dimension):
        node = node_array[row][column]
        for i in xrange(row - 1, row + 2):
          for j in xrange(column - 1, column + 2):
            # do not establish link to self, nodes out of bounds, or nodes
            # that would raise redundancy level
            if row == i and column == j:
              continue
            if i < 0 or i >= dimension or j < 0 or j >= dimension:
              continue
            if (i, j) == (row - 1, column + 1):
              continue
            if (i, j) == (row + 1, column - 1):
              continue
            node.addLink(node_array[i][j])
  elif redundancyLevel == 4:
    if not quiet:
		  print '<--------------->'
		  print 'Redundancy Level = 4'
		  print '<--------------->'
		  print '         \|/'
		  print 'Links:  --*--'
		  print '         /|\\'
		  print '<--------------->'
    for row in xrange(dimension):
      for column in xrange(dimension):
        node = node_array[row][column]
        for i in xrange(row - 1, row + 2):
          for j in xrange(column - 1, column + 2):
            # do not establish link to self, nodes out of bounds, or nodes
            # that would raise redundancy level
            if row == i and column == j:
              continue
            if i < 0 or i >= dimension or j < 0 or j >= dimension:
              continue
            node.addLink(node_array[i][j])
  else:
    raise Exception('Can\'t yet support any R other than 2, 3 or 4.')

  return node_array

def synchronized_attack(node_array, P_k):
	"""P_k is the Probability that the missile aimed at each node kills the node"""
	from random import random
	for row in node_array:
		for node in row:
			if random() < P_k:
				node.destroy()

def get_largest_surviving_group(node_array):
	"""The largest surviving group is defined as the largest subset 
		of still connected nodes after the synchronized_attack"""
	from collections import deque

	unassigned_living_nodes = []
	for row in node_array:
		for node in row:
			if node.isAlive():
				unassigned_living_nodes.append(node)

	surviving_groups = []
	while len(unassigned_living_nodes) > 0:
		group = []

		# add the first node of the group and build the 
		# first part of the fringe to search for more
		first = unassigned_living_nodes.pop()
		group.append(first)
		# fringe = deque(first.neighbors) #queue
                fringe = deque(first.getReachableNeighbors())

		# now follow the trail of surviving links through the 
		# rest of the connected nodes to form the whole group
		while len(fringe) > 0:
			curr = fringe.popleft()
			# remove this fringe neighbor from the unassigned group
			# as we are about to assign it to a group
			unassigned_living_nodes.remove(curr)
			group.append(curr)
			# grow the fringe to whatever existing connections remain
			# fringe.extend(filter(lambda n : n not in group and n not in fringe, curr.neighbors))
			fringe.extend(filter(lambda n : n not in group and n not in fringe, curr.getReachableNeighbors()))

		# this group gets added to the list of groups
		surviving_groups.append(group)

	if len(surviving_groups) == 0:  
		return []
	return max(surviving_groups, key = lambda g : len(g))

def calculate_survivability(node_array, largest_surviving_group):
	return len(largest_surviving_group) / float(len(node_array) ** 2)

def gen_graphviz_graph(node_array, output_file_name, largest_surviving_group = []):
  graphviz_tmpl = \
    "strict graph {{\n" \
    "      node [label = \"\"  shape=point  width=0.3];\n" \
    "      edge [arrowhead = \"none\"]\n" \
    "{ranks}\n" \
    "{node_edges}\n" \
    "{destroyed_nodes}\n" \
    "{nodes_from_largest_surviving_group}\n" \
    "}}"
  node_list_to_id_str_list_func = lambda node_list: " ".join(map(str, map(id, node_list)))
  same_rank_tmpl = "      {{ rank=same {node_id_list} }}"
  formatted_ranks = "\n".join(map(lambda fmtd: same_rank_tmpl.format(node_id_list = fmtd), map(node_list_to_id_str_list_func, node_array)))
  node_outgoing_edges_tmpl = \
    "      {node_id} -- {{ {neighbor_id_list} }}"
  node_to_outgoing_edges_func = \
    lambda node, reachable: node_outgoing_edges_tmpl \
      .format( \
        node_id = id(node), \
        neighbor_id_list = node_list_to_id_str_list_func(node.getReachableNeighbors(reachable)))
  node_to_visible_outgoing_edges_func = lambda node: node_to_outgoing_edges_func(node, True)
  node_to_invisible_outgoing_edges_func = lambda node: node_to_outgoing_edges_func(node, False) + " [style=dotted]"
  formatted_edges_list, destroyed_nodes_list = \
          zip(* # Apparently this is the "Pythonic" way to unzip tuples.
            [(node_to_visible_outgoing_edges_func(node) + "\n" + node_to_invisible_outgoing_edges_func(node), 
              "      {node_id} [shape=circle color=red]".format(node_id = id(node)) if node.destroyed == True else "")
                for row in node_array for node in row])
  formatted_edges = '\n'.join(formatted_edges_list)
  formatted_destroyed_nodes = '\n'.join(filter(lambda s: len(s) > 0, destroyed_nodes_list))
  formatted_nodes_from_largest_surviving_group = \
          '\n'.join(['      {node_id} [color=green]'.format(node_id = id(node)) for node in largest_surviving_group])
  graphviz_file_content = graphviz_tmpl.format(
          ranks = formatted_ranks, 
          node_edges = formatted_edges, 
          destroyed_nodes = formatted_destroyed_nodes,
          nodes_from_largest_surviving_group = formatted_nodes_from_largest_surviving_group)
  with open(output_file_name, 'w') as output_file:
    output_file.write(graphviz_file_content)

def print_network(node_array):
	for row in node_array:
		for node in row:
			print 'A ' if node.isAlive() else 'X ',
		print

def print_largest_surviving_group(node_array, largest_surviving_group):
	for row in node_array:
		for node in row:
			if node in largest_surviving_group:
				print 'A ',
			else:
				print '  ',
		print

def test(P_k = 0.4, dimension = 18, redundancyLevel = 2, quiet = False): 
  node_array = build_node_array(dimension, redundancyLevel, quiet)
  if not quiet:
    print '<--------------->'
    gen_graphviz_graph(
      node_array,
      'graphviz-sim-visualizations/simulation-dim={dim}-redundLev={redundLev}.gv'.format(
        dim = dimension,
        redundLev = redundancyLevel))
    print '<--------------->'
  synchronized_attack(node_array, P_k)
  if not quiet:
    print 'P_k = {0}'.format(P_k)
    print '<--------------->'
    print_network(node_array)
    print '<--------------->'
  largest_surviving_group = get_largest_surviving_group(node_array)
  if not quiet:
    print_largest_surviving_group(node_array, largest_surviving_group)
    print '<--------------->'
  survivability = calculate_survivability(node_array, largest_surviving_group)
  if not quiet:
    print 'Survivability = {0}'.format(survivability)
    print '<--------------->'
    gen_graphviz_graph(
      node_array,
      'graphviz-sim-visualizations/simulation-P_k={P_k}-dim={dim}-redundLev={redundLev}.gv'.format(
        P_k = P_k,
        dim = dimension,
        redundLev = redundancyLevel),
      largest_surviving_group)
  return survivability



def RunExperiment(samples = 20, R = 2):
    from pylab import linspace
    
    results = []
    
    # must run the test over a large, evenly spaced range of p_k's
    for p_k in linspace(0.0, 1.0, 50):
        total_survivability = 0
        for _ in xrange(samples):
            total_survivability += test(p_k, redundancyLevel = R, quiet = True)
        results.append(total_survivability / samples) # append average

    return results

def DisplayResults(experiment_result_lists):
    from pylab import linspace, plot, xlabel, ylabel, title, show, legend, ylim
    from scipy.interpolate import interp1d
    
    for R, results in experiment_result_lists:
            p_k_list = linspace(0.0, 1.0, len(results))
            f = interp1d(p_k_list, results, kind='cubic') #estimate the interpolation function
            xnew = linspace(0.0, 1.0, len(results)*10) #create a new set of many more x-values to get data from f
            plot(xnew, f(xnew), label = 'R={0}'.format(R)) #plot experimental values, after interpolation

    plot([0,0.5,1],[1,0.5,0], label = 'Optimum') #plot optimal expected line
            
    title('Baran\'s Monte Carlo Simulation')
    xlabel('Single Node Probability of Destruction')
    ylabel('"Survivability"\nLargest Fraction of Stations in Communication')
    legend(loc = "upper right")

    ylim(0, 1)
    show()
    
    
if __name__ == '__main__':
  import sys
  # args passed in as P_k, dimension, redundancyLevel

  if len(sys.argv) == 1:
    experiment_results_list = []
    for R in xrange(1,5):
      experiment_results_list.append((R, RunExperiment(20, R)))
      DisplayResults(experiment_results_list)
  else:
    print "Example Network Survivability Simulation:"
    if len(sys.argv) == 2:
      test(float(sys.argv[1]))
    elif len(sys.argv) == 3:
      test(float(sys.argv[1]), int(sys.argv[2]))
    else:
      test(float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
