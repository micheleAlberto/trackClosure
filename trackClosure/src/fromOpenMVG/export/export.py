
"""
export 
strategy: export matches, not tracks
why: openMVG import matches without modifications. Patching would be needed to import tracks.
How: 
    1)for each track select a path that connect all the keypoints
    2)for each segment of the path generate a match
    3)export matches in the format of matches.f.txt
    4)run openMVG to reconstruct from matches

#Path selection
select keypoints closer to the centroid of keypoints of each image
chain keypoints in growing order of image identifier
#matches.f.txt
{im_a} {im_b}\n
{n: number of matches in (im_a im_b)}\n
{kp_a_1} {kp_b_1}
{kp_a_2} {kp_b_2}
...
{kp_a_n} {kp_b_n}

# openMVG tracking algorithm
``` cpp

  /// Build tracks for a given series of pairWise matches
  bool Build( const PairWiseMatches &  map_pair_wise_matches)
  {
    typedef std::set<indexedFeaturePair> SetIndexedPair;
    SetIndexedPair myset;
    for (PairWiseMatches::const_iterator iter = map_pair_wise_matches.begin();
      iter != map_pair_wise_matches.end();
      ++iter)
    {
      const size_t & I = iter->first.first;
      const size_t & J = iter->first.second;
      const std::vector<IndMatch> & vec_FilteredMatches = iter->second;
      // We have correspondences between I and J image index.

      for( size_t k = 0; k < vec_FilteredMatches.size(); ++k)
      {
        // Look if one of the feature already belong to a track :
        myset.insert(std::make_pair(I,vec_FilteredMatches[k]._i));
        myset.insert(std::make_pair(J,vec_FilteredMatches[k]._j));
      }
    }

    // Build the node indirection for each referenced feature
    MapIndexNode my_Map;
    my_Map.reserve(myset.size());
    reverse_my_Map.reserve(myset.size());
    for (SetIndexedPair::const_iterator iter = myset.begin();
      iter != myset.end();
      ++iter)
    {
      lemon::ListDigraph::Node node = g.addNode();
      my_Map.push_back( std::make_pair(*iter, node));
      reverse_my_Map.push_back( std::make_pair(node,*iter));
    }

    // Sort the flat_pair_map
    my_Map.sort();
    reverse_my_Map.sort();

    // Add the element of myset to the UnionFind insert method.
    index = std::auto_ptr<IndexMap>( new IndexMap(g) );
    myTracksUF = std::auto_ptr<UnionFindObject>( new UnionFindObject(*index));
    for (ListDigraph::NodeIt it(g); it != INVALID; ++it) {
      myTracksUF->insert(it);
    }

    // Make the union according the pair matches
    for (PairWiseMatches::const_iterator iter = map_pair_wise_matches.begin();
      iter != map_pair_wise_matches.end();
      ++iter)
    {
      const size_t & I = iter->first.first;
      const size_t & J = iter->first.second;
      const std::vector<IndMatch> & vec_FilteredMatches = iter->second;
      // We have correspondences between I and J image index.

      for( size_t k = 0; k < vec_FilteredMatches.size(); ++k)
      {
        indexedFeaturePair pairI(I,vec_FilteredMatches[k]._i);
        indexedFeaturePair pairJ(J,vec_FilteredMatches[k]._j);
        myTracksUF->join( my_Map[pairI], my_Map[pairJ] );
      }
    }
    return false;
  }

```
Code ported to python
``` python
map_indexToNode = []
_map_nodeToIndex = []
kp_key_set = set() # SetIndexedPair allFeatures;
for M in matches.iterItems():
    I,J = M[0]
    vec_FilteredMatches = M[1]
    for k in range(len(vec_FilteredMatches)):
        kp_key_set.add((I, vec_FilteredMatches[k][0]))
        kp_key_set.add((J, vec_FilteredMatches[k][1]))

for kp in kp_key_set:
    n = graph.node()
    map_indexToNode.append((kp, n))
    _map_nodeToIndex.append((n, kp))

map_indexToNode.sort();
_map_nodeToIndex.sort();
ufo = UnionFindObject(graph)
for n in graph:
    ufo.insert(n)

for M in matches:
    I,J = M[0]
    vec_FilteredMatches = M[1]
    for m in vec_FilteredMatches:   
        pair_I= (M[0],m[0])
        pair_J= (M[1],m[1])
        ufo.join(
            map_indexToNode[pair_I],
            map_indexToNode[pair_J])

```
"""

def one(partition, centroid_functor):
    chains = []
    for t_id in partition.points.keys():
        T = partition.points[t_id]
        chain = []
        for im_id in sorted(T.views.keys()):
            best_keypoint = centroid_functor(T.views[im_id])
            chain+= best_keypoint.key()
        chains.append(chain)
    return chains

def two(chains):
    matches = {}
    for ch in chains:
        for i in range(len(ch)-1):
            kp_I,kp_J = ch[i:i+2]
            im_pair = (kp_I[0], kp_J[0])
            #I,J = im_pair
            if im_pair in matches:
                matches[im_pair].append( (kp_I[1], kp_J[1]))
            else:
                matches[im_pair] = [(kp_I[1], kp_J[1])]
    return matches

def three(matches,write_functor):
    for M in matches:
        pair_header="{} {}\n".format(M[0],M[1])
        lenght="{}\n".format(len(matches[M]))
        body=""
        for m in matches[M]:
            body+="{} {}\n".format(m[0],m[1])
        match_block=pair_header+lenght+body
        write_functor(match_block)
    return

def three2(matches,file_name):
    with open(file_name,'w') as fout:
         wr_f=lambda x:fout.write(x)
         three(matches,wr_f)

            
