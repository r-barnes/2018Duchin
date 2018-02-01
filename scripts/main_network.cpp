#include "compactnesslib/compactnesslib.hpp"
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <unordered_map>
#include <vector>



class Timer {
 private:
  typedef std::chrono::high_resolution_clock clock;
  typedef std::chrono::duration<double, std::ratio<1> > second;
  std::chrono::time_point<clock> start_time;
 public:
  Timer()        { start_time = clock::now(); }
  void reset()   { start_time = clock::now(); }
  double elapsed() const { return std::chrono::duration_cast<second> (clock::now() - start_time).count(); }
};



int main(int argc, char **argv) {
  Timer timer_overall;

  if(argc<9){
    std::cerr<<"Syntax: "<<argv[0]<<" -sub <Subunit File> -sup <Superunit File> -outpre <Output prefix> -<shp/noshp> -<printparent/noprintparent>"<<std::endl;
    return -1;
  }

  std::vector<std::string> in_sub_filenames;
  std::vector<std::string> in_sup_filenames;
  std::string output_prefix;

  bool output_shapefile = false;
  bool print_parent     = false;

  int state = 0;
  for(int i=0;i<argc;i++){
    if(argv[i]==std::string("-sub")){
      state = 1;
      continue;
    } else if(argv[i]==std::string("-sup")){
      state = 2;
      continue;
    } else if(argv[i]==std::string("-outpre")){
      state = 3;
      continue;
    } else if(argv[i]==std::string("-shp")){
      output_shapefile = true;
      state            = 0;
      continue;
    } else if(argv[i]==std::string("-noshp")){
      output_shapefile = false;
      state            = 0 ;
      continue;
    } else if(argv[i]==std::string("-printparent")){
      print_parent = true;
      state        = 0;
      continue;
    } else if(argv[i]==std::string("-noprintparent")){
      print_parent = false;
      state        = 0;
      continue;
    }

    switch(state){
      case 0: //Haven't found a command yet
        break;
      case 1: //Collecting subunit files
        in_sub_filenames.emplace_back(argv[i]);
        break;
      case 2: //Collecting superunit files
        in_sup_filenames.emplace_back(argv[i]);
        break;
      case 3: //Collecting output file
        output_prefix = argv[i];
        break;
      default:
        throw std::logic_error("Should not reach this point!");
    }
  }

  complib::GeoCollection gc_sub;
  complib::GeoCollection gc_sup;

  for(const auto &subfn: in_sub_filenames){
    std::cout<<"Reading subunit file '"<<subfn<<"'..."<<std::endl;
    auto this_sub = complib::ReadShapefile(subfn);
    std::cout<<"sub size = "<<this_sub.size()<<std::endl;
    gc_sub.v.insert(
      gc_sub.end(),
      std::make_move_iterator(this_sub.begin()),
      std::make_move_iterator(this_sub.end())
    );
  }

  for(const auto &supfn: in_sup_filenames){
    std::cout<<"Reading superunit file '"<<supfn<<"'..."<<std::endl;
    auto this_sup = complib::ReadShapefile(supfn);
    std::cout<<"sup size = "<<this_sup.size()<<std::endl;
    gc_sup.v.insert(
      gc_sup.end(),
      std::make_move_iterator(this_sup.begin()),
      std::make_move_iterator(this_sup.end())
    );
  }


  //Pre-build clipper paths for all of the subunits and superunits. These will
  //be used to determine overlaps.
  std::cout<<"Clipperifying..."<<std::endl;
  gc_sup.clipperify();
  gc_sub.clipperify();

  std::cout<<"Calculating parent overlaps..."<<std::endl;
  CalcParentOverlap(
    gc_sub,
    gc_sup,  
    0.997,    //complete_inclusion_thresh
    0.003,    //not_included_thresh
    120,      //edge_adjacency_dist      
    print_parent
  );

  // //Finds external children who still have 100% overlap with their parent
  // std::cout<<"Finding external children..."<<std::endl;
  // FindExternalChildren(
  //   gc_sub,
  //   gc_sup,
  //   250,      //max_boundary_pt_dist
  //   500       //edge_adjacency_dist  
  // );

  std::cout<<"Finding neighbouring districts..."<<std::endl;
  FindNeighbouringDistricts(
    gc_sub,
    100,  //max_neighbour_pt_dist
    200   //expand_bb_by
  );

  std::ofstream fout(output_prefix+".scores");
  for(const auto &sub: gc_sub){
    for(const auto &kv: sub.props)
      fout<<kv.first<<"="<<kv.second<<"~";
    fout<<std::endl;
  }

  if(output_shapefile){
    //complib::CalculateAllBoundedScores(gc_sub, gc_sup, join_on);
    //complib::CalculateAllUnboundedScores(gc_sub);
    complib::WriteShapefile(gc_sub,output_prefix);
  }

  std::cout<<"Overall time = "<<timer_overall.elapsed()<<" s"<<std::endl;

  return 0;
}