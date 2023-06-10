#include<bits/stdc++.h>

using namespace std;

void push(int a);
int  pop();
int getmin();
int top();

stack< int > s;
int minEle; 

int main() 
{
    s.push(2);
}

int getmin () {
    if(s.size() == 0) {
        return -1;
    }
    return minEle;
}

void push( int a) {
    if (s.size() == 0 ) {
        s.push(a);
        minEle = a;
    }
    else
        if( a >= minEle) {
            s.push(a);
        }
        else if ( a < minEle ) {
            s.push( 2 * a - minEle); // this is the main formula 2*x - min element
            minEle = a;
        }
}

int pop() {
    if (s.size() == 0 ) {
        return -1;
    }
    else {
        if (s.top() >= minEle) {
            s.pop();
        }
        else if (s.top() < minEle) {
            minEle =2 * minEle - s.top(); // this is another main formula( 2 * min element - s.top ) 
            s.pop(); 
        } 
    }        
}

int top() {
    if( s.size() == 0 ) {
        return -1;
    }
    else 
        if ( s.top() > minEle) {
        return s.top();
    }
        else if ( s.top() < minEle) { // if we get minimum ele in top we reutrn minEle
        return minEle;
    }
}
