SOURCES = $(wildcard compactnesslib/*.cpp) $(wildcard compactnesslib/shapelib/*.cpp) $(wildcard compactnesslib/lib/*.cpp) network_nonboost.cpp Timer.cpp
OBJECTS = $(SOURCES:.cpp=.o)

CXX_FLAGS = --std=c++11 -march=native -mtune=native -g -O3 -DNDEBUG -DDOCTEST_CONFIG_DISABLE -Wall -Wpedantic -fopenmp

all: $(OBJECTS)
	$(CXX) $(CXX_FLAGS) $(OBJECTS) -o net_compact.exe

%.o: %.cpp
	$(CXX) -c $(CXX_FLAGS) $< -o $@ 

clean:
	rm -rf compactness.exe compactnesslib/*.o compactnesslib/shapelib/*.o compactnesslib/lib/*.o *.o