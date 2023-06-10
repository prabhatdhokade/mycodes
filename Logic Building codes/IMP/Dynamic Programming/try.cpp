
#include<bits/stdc++.h>

using namespace std;

int solve(int n)
    {
        // your code here
        int t[n+1];
        t[0] = 1;
        t[1] = 1;
        
        for(int i =2;i<=n;i++) {
            t[i] = t[i-1]+ t[i-2];
        }
        return t[n];
    }

int main()
{
    int n;
    cin>>n;
    // memset(t,-1,sizeof(t));
    cout<<solve(n);
    
   
}
