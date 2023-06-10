/* Given a string S, we can transform every letter individually to be lowercase or uppercase to create another string.  Return a list of all possible strings we could create.

Examples:
Input: S = "a1b2"
Output: ["a1b2", "a1B2", "A1b2", "A1B2"]

Input: S = "3z4"
Output: ["3z4", "3Z4"]

Input: S = "12345"
Output: ["12345"]
*/
// IMP Problem
#include<bits/stdc++.h>

using namespace std;

void solve(string ip,string op) {
    if(ip.size() == 0) {
        cout<<op<<",";
        return;
    }
    else if(isalpha(ip[0])) {
        string op1=op;
        string op2=op;
        op1.push_back(tolower(ip[0]));
        op2.push_back(toupper(ip[0]));
        ip.erase(ip.begin()+0);
        solve(ip,op1);
        solve(ip,op2);
        return;
    }
    else 
    {
        string op1 =op;
        op1.push_back(ip[0]);
        ip.erase(ip.begin()+ 0);
        solve(ip,op1);
        return;
    }
}


int main() 
{
    string s1;
    cin>>s1;
    string s2 ="";
    solve(s1,s2);
}