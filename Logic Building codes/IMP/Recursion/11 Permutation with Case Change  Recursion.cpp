/* Print all permutations of a string keeping the sequence but changing cases.

Examples:

Input : ab
Output : ab, aB, Ab, AB,*/

#include<bits/stdc++.h>

using namespace std;

void solve(string ip,string op) {
    if( ip.size() == 0) {
        cout<<op<<",";
        return;
    }

    string op1 = op;
    string op2 = op;
    op1.push_back(ip[0]); // inititilize it to first index
    op2.push_back(toupper(ip[0])); // this gives capital letter
    ip.erase(ip.begin() +0);

    solve(ip,op1);
    solve(ip,op2);
    return;
}

int main()
{
    string s1;
    cin>>s1;
    string s2 =" ";
    solve(s1,s2);
}