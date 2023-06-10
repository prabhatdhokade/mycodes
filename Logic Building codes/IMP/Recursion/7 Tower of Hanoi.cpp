// try other problems also
// treveling salesman problem
// Graph coloring 
//sum of subsets

// exponentional complexity

#include<bits/stdc++.h>
using namespace std;
// sr = sorce rod
// hr = helping rod
// ds = destination rod
int toh(int n, int sr, int hr,int ds,int &count) {
    count++;
    if(n==1){
        //cout<<"("<<sr<<","<<ds<<")";
        return 1;
    }
    else{
        toh(n-1,sr,ds,hr,count);
        //cout<<"("<<sr<<","<<ds<<")";
        toh(n-1,hr,sr,ds,count);
    }
    return count;
    // time complexity = O(2^n)
}

int main()
{
    int n;
    cin>>n;
    int count= 0;

    toh(n, 1,2,3,count);
    cout<<count;
}