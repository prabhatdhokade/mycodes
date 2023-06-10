#include<bits/stdc++.h>

using namespace std;
void fib(int n) {
    if(n == 1 || n ==0 ) {
        return ;
    }
    else     
     cout<< fib(n-1)+fib(n-2);
}

int main()
{
    int n ;
    cin>>n;

    fib(n);
}