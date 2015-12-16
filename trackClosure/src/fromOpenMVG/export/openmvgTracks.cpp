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

