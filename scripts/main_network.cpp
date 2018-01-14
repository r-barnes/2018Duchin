#include "compactnesslib/compactnesslib.hpp"
#include "Timer.hpp"
#include <iostream>
#include <fstream>
#include <iomanip>
#include <vector>
#include <unordered_map>
#include <iterator>

int main(int argc, char **argv) {
  Timer timer_overall;

  if(argc<7){
    std::cerr<<"Syntax: "<<argv[0]<<" -sub <Subunit File> -sup <Superunit File> -outsub <Output subunit file>"<<std::endl;
    return -1;
  }

  std::vector<std::string> in_sub_filenames;
  std::vector<std::string> in_sup_filenames;
  std::string out_sub_filename;

  int state = 0;
  for(int i=0;i<argc;i++){
    if(argv[i]==std::string("-sub")){
      state = 1;
      continue;
    } else if(argv[i]==std::string("-sup")){
      state = 2;
      continue;
    } else if(argv[i]==std::string("-outsub")){
      state = 3;
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
        out_sub_filename = argv[i];
        break;
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

  std::cout<<"Clipperifying..."<<std::endl;
  gc_sup.clipperify();
  gc_sub.clipperify();

  std::cout<<"Calculating parent overlaps..."<<std::endl;
  CalcParentOverlap(gc_sub, gc_sup);

  std::cout<<"Finding neighbouring districts..."<<std::endl;
  FindNeighbouringDistricts(gc_sub);


  std::ofstream fout(out_sub_filename);
  for(const auto &sub: gc_sub){
    for(const auto &kv: sub.props)
      fout<<kv.first<<"="<<kv.second<<"~";
    fout<<std::endl;
  }

  //complib::CalculateAllBoundedScores(gc_sub, gc_sup, join_on);
  //complib::CalculateAllUnboundedScores(gc_sub);
  //complib::WriteShapefile(gc_sub,out_sub_filename);

  std::cout<<"Overall time = "<<timer_overall.elapsed()<<" s"<<std::endl;

  return 0;
}