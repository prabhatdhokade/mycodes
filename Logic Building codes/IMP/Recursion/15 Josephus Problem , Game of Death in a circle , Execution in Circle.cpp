/* There are n people standing in a circle (numbered clockwise 1 to n) waiting 
to be executed. The counting begins at point 1 in the circle and proceeds around 
the circle in a fixed direction (clockwise). In each step, a certain number of people 
are skipped and the next person is executed. The elimination proceeds around the 
circle (which is becoming smaller and smaller as the executed people are removed),
 until only the last person remains, who is given freedom.
Given the total number of persons n and a number k which indicates that k-1 persons
 are skipped and kth person is killed in circle. The task is to choose the place in 
 the initial circle so that you are the last one remaining and so survive.
Consider if n = 5 and k = 2, then the safe position is 3.
Firstly, the person at position 2 is killed, then person at position 4 is killed,
 then person at position 1 is killed. Finally, the person at position 5 is killed. 
 So the person at position 3 survives.*/

#include<bits/stdc++.h>

using namespace std;

void solve(int index,int &ans,int k,vector<int> v) {
    if(v.size() == 1) {
        ans = v[0];
        return;
    }
    index = (index + k) % v.size(); // for avoiding integer overflow 
    v.erase(v.begin() + index); // delete the index and move on
    solve(index,ans,k,v);
    return;
}

int main() 
{
    int n;
    int k;
    cin>>n>>k;
    int ans = -1;
    int index = 0;
    k = k-1;
    vector<int> v;
    for(int i=1; i<=n; i++) {
        v.push_back(i);
    } 
    solve(index,ans,k,v);
    cout<<ans;
}