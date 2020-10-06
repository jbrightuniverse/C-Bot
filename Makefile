CXX=g++
TARGET=main
CXXFLAGS=-O2 -march=native -std=c++17
SRCS=$(shell find . -path "*.cpp")
OBJS=$(patsubst %.cpp, %.o, $(SRCS))
LDFLAGS=-lpthread
.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $^ -o $(TARGET) $(LDFLAGS)

./%.o: ./%.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -fr $(TARGET) $(OBJS)
