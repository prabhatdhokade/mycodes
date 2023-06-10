#include<bits/stdc++.h> 

using namespace std;

void solve(int ones,int zeros, int n, string op) {
    
    if( n == 0) {
    cout<< op << ",";
    return;
    }

    string op1 = op;
    op1.push_back('1');
    solve( ones+1, zeros, n-1, op1);   // why one+1 u have chek this out

    if(ones > zeros) {
        string op2 = op;
        op2.push_back('0');
        solve(ones, zeros+1,n-1,op2); // why zero+1 u have to chek this out 
        // why n-1 u have to chek this out
    }
    return;
}

int main()
{
    int n;
    cin >> n;
    string op = "";
    int ones = 0;
    int zeros = 0;

    solve(ones,zeros,n,op);
}