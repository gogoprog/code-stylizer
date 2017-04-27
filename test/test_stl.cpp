#include <iostream>
#include <vector>
#include "../out/vector.h"

int main()
{
    Std::Vector<int, Std::Allocator<int>> myInts;

    myInts.pushBack(0);
    myInts.pushBack(1);
    myInts.pushBack(2);

    for(Std::Vector<int, Std::Allocator<int>>::Iterator it = myInts.begin(); it != myInts.end(); ++it)
    {
        std::cout << *it << std::endl;
    }

    return 0;
}